"""Sensori: livello, tendenza, livello di allerta, ultima misura."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import WaterLevelEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            LevelSensor(c),
            TrendSensor(c),
            AlertLevelSensor(c),
            LastMeasureSensor(c),
            *[ThresholdSensor(c, n) for n in (1, 2, 3)],
        ]
    )


class ThresholdSensor(WaterLevelEntity, SensorEntity):
    """Valore della soglia N (m), definito dalla Regione per la stazione."""

    _attr_native_unit_of_measurement = "m"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, number: int) -> None:
        super().__init__(coordinator, f"threshold_{number}")
        self._number = number

    @property
    def native_value(self) -> float | None:
        value = getattr(self.coordinator.data, f"threshold_{self._number}")
        return value or None  # 0 = soglia non definita


class LevelSensor(WaterLevelEntity, SensorEntity):
    _attr_native_unit_of_measurement = "m"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "level")

    @property
    def native_value(self) -> float:
        return self.coordinator.data.level

    @property
    def extra_state_attributes(self) -> dict:
        d = self.coordinator.data
        return {
            "threshold_1": d.threshold_1,
            "threshold_2": d.threshold_2,
            "threshold_3": d.threshold_3,
            "station_id": self.coordinator.station_id,
        }


class TrendSensor(WaterLevelEntity, SensorEntity):
    _attr_native_unit_of_measurement = "m/h"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:trending-up"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "trend")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.trend_m_h


class AlertLevelSensor(WaterLevelEntity, SensorEntity):
    """0 = nessuna soglia superata, 1/2/3 = soglia (gialla/arancione/rossa)."""

    _attr_icon = "mdi:waves-arrow-up"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "alert_level")

    @property
    def native_value(self) -> int:
        return self.coordinator.data.alert_level


class LastMeasureSensor(WaterLevelEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "last_measure")

    @property
    def native_value(self) -> datetime:
        return self.coordinator.data.measured_at
