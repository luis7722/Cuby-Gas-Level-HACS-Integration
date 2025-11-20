"""Sensors for Cuby Gas Level."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_DEVICE_IDS
from .coordinator import CubyCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: CubyCoordinator = data["coordinator"]

    entities: list[CubyGasLevelSensor] = [
        CubyGasLevelSensor(coordinator, device_id) for device_id in entry.data[CONF_DEVICE_IDS]
    ]

    async_add_entities(entities)


class CubyGasLevelSensor(CoordinatorEntity[CubyCoordinator], SensorEntity):
    """Sensor for a single Cuby device gas level."""

    _attr_icon = "mdi:gas-cylinder"
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator: CubyCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"Cuby Gas Level {device_id}"
        self._attr_unique_id = f"cuby_gas_level_{device_id}"

    @property
    def native_value(self) -> float | None:
        entry = self._entry_data
        return entry.get("level") if entry else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        entry = self._entry_data
        if not entry:
            return None
        return {"device_id": self._device_id, "last_update": entry.get("timestamp")}

    @property
    def _entry_data(self) -> dict | None:
        return self.coordinator.data.get(self._device_id) if self.coordinator.data else None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()