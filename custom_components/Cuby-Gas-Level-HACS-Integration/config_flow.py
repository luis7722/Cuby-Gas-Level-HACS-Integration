"""Config flow for Cuby Gas Level."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_DEVICE_IDS,
    TOKEN_URL_TEMPLATE,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_credentials(hass: HomeAssistant, email: str, password: str) -> bool:
    """Validate that we can obtain a token with provided credentials."""
    url = TOKEN_URL_TEMPLATE.format(email=email)
    payload = {"password": password, "expiration": 3600}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Token validation failed: %s", await resp.text())
                    return False
                data = await resp.json()
                return bool(data.get("token"))
    except Exception as e:
        _LOGGER.error("Error validating credentials: %s", e)
        return False


class CubyGasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cuby Gas Level."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input.get(CONF_EMAIL, "").strip()
            password = user_input.get(CONF_PASSWORD, "").strip()
            device_ids_raw = user_input.get(CONF_DEVICE_IDS, "").strip()

            if not email or not password or not device_ids_raw:
                errors["base"] = "missing_fields"
            else:
                # Parse comma-separated device ids
                device_ids = [d.strip() for d in device_ids_raw.split(",") if d.strip()]

                valid = await _validate_credentials(self.hass, email, password)
                if not valid:
                    errors["base"] = "invalid_auth"
                else:
                    data = {
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                        CONF_DEVICE_IDS: device_ids,
                    }
                    return self.async_create_entry(title=f"Cuby Gas ({email})", data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_DEVICE_IDS): str,  # comma-separated: e.g. "ABC123,XYZ789"
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)