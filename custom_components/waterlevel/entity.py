"""Entita' base."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WaterLevelCoordinator


class WaterLevelEntity(CoordinatorEntity[WaterLevelCoordinator]):
    """Entita' legata alla stazione."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: WaterLevelCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.station_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.station_id)},
            name=coordinator.data.name,
            manufacturer="Regione Emilia-Romagna / ARPAE",
            model="Idrometro",
            entry_type=None,
        )
