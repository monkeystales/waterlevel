"""Binary sensor: una per ciascuna soglia di allerta."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import WaterLevelEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ThresholdBinarySensor(c, n) for n in (1, 2, 3)])


class ThresholdBinarySensor(WaterLevelEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, number: int) -> None:
        super().__init__(coordinator, f"threshold_{number}_exceeded")
        self._number = number

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.alert_level >= self._number
