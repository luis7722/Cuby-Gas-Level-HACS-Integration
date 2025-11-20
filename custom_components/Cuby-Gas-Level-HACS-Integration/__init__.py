"""Cuby Gas Level integration bootstrap."""
from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import CubyCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up via configuration.yaml (not used; we rely on config_flow)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cuby Gas Level from a config entry."""
    coordinator = CubyCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
    }

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    _LOGGER.debug("Cuby Gas Level integration set up for entry %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded