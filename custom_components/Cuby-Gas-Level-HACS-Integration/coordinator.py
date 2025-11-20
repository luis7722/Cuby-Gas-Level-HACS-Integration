"""DataUpdateCoordinator for Cuby Gas Level."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta, datetime, timezone
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_DEVICE_IDS,
    DEFAULT_TOKEN_EXP_SECONDS,
    UPDATE_INTERVAL_SECONDS,
    TOKEN_URL_TEMPLATE,
    GAS_URL_TEMPLATE,
)

_LOGGER = logging.getLogger(__name__)


class CubyCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that manages token and gas level polling."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self.hass = hass
        self.email: str = config[CONF_EMAIL]
        self.password: str = config[CONF_PASSWORD]
        self.device_ids: list[str] = config[CONF_DEVICE_IDS]

        self._token: str | None = None
        self._token_expiration: datetime | None = None

        super().__init__(
            hass,
            _LOGGER,
            name="Cuby Gas Level",
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

        # data will be shaped as { device_id: { "level": float | None, "timestamp": str | None } }
        self.data: dict = {}

    async def _async_get_token(self, session: aiohttp.ClientSession) -> None:
        """Retrieve a JWT token and store expiration."""
        url = TOKEN_URL_TEMPLATE.format(email=self.email)
        payload = {"password": self.password, "expiration": DEFAULT_TOKEN_EXP_SECONDS}

        try:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise UpdateFailed(f"Token request failed: {resp.status} - {text}")

                data = await resp.json()
                token = data.get("token")
                exp_seconds = data.get("expiration", DEFAULT_TOKEN_EXP_SECONDS)

                if not token:
                    raise UpdateFailed("Token missing in response")

                self._token = token
                # Set local expiration timestamp slightly earlier to proactively refresh
                self._token_expiration = datetime.now(timezone.utc) + timedelta(seconds=max(30, exp_seconds - 30))
                _LOGGER.debug("Token acquired; expires at %s", self._token_expiration)

        except asyncio.TimeoutError as e:
            raise UpdateFailed(f"Token request timeout: {e}") from e
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Token request client error: {e}") from e

    def _token_is_expired(self) -> bool:
        if not self._token or not self._token_expiration:
            return True
        return datetime.now(timezone.utc) >= self._token_expiration

    async def _async_fetch_gas_level(
        self, session: aiohttp.ClientSession, device_id: str
    ) -> tuple[float | None, str | None]:
        """Fetch gas level for a specific device_id."""
        if not self._token:
            return None, None

        url = GAS_URL_TEMPLATE.format(cuby_id=device_id, jwt=self._token)

        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    _LOGGER.warning("Gas level fetch failed for %s: %s - %s", device_id, resp.status, text)
                    return None, None

                data = await resp.json()
                level = data.get("level")
                timestamp = data.get("timestamp")
                return level, timestamp

        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout fetching gas level for %s", device_id)
            return None, None
        except aiohttp.ClientError as e:
            _LOGGER.warning("Client error for %s: %s", device_id, e)
            return None, None

    async def _async_update_data(self) -> dict:
        """Update coordinator data: refresh token if needed, then poll all devices."""
        async with aiohttp.ClientSession() as session:
            # Refresh token if expired or missing
            if self._token_is_expired():
                await self._async_get_token(session)

            # Poll all devices in parallel
            tasks = [self._async_fetch_gas_level(session, dev_id) for dev_id in self.device_ids]
            results = await asyncio.gather(*tasks, return_exceptions=False)

        updated: dict = {}
        for dev_id, (level, timestamp) in zip(self.device_ids, results):
            updated[dev_id] = {"level": level, "timestamp": timestamp}

        # Keep the full dict for all sensors to read
        self.data = updated
        return updated