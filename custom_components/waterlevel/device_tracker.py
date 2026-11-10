"""Posizione della stazione, visibile nella mappa di Home Assistant."""
from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import WaterLevelEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    c = hass.data[DOMAIN][entry.entry_id]
    if c.data.latitude is not None and c.data.longitude is not None:
        async_add_entities([StationLocation(c)])


class StationLocation(WaterLevelEntity, TrackerEntity):
    _attr_icon = "mdi:waves"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "location")

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        return self.coordinator.data.latitude

    @property
    def longitude(self) -> float | None:
        return self.coordinator.data.longitude

    @property
    def extra_state_attributes(self) -> dict:
        return {"level": self.coordinator.data.level}
