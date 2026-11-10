"""DataUpdateCoordinator per il livello idrometrico."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WaterLevelApiError, async_fetch_stations
from .const import CONF_STATION_ID, DOMAIN, STALE_AFTER, TREND_WINDOW_MS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


@dataclass
class StationData:
    """Dati correnti della stazione."""

    name: str
    level: float
    measured_at: datetime
    threshold_1: float
    threshold_2: float
    threshold_3: float
    trend_m_h: float | None
    latitude: float | None = None
    longitude: float | None = None

    @property
    def alert_level(self) -> int:
        """0 = sotto soglia 1, 1..3 = soglia superata."""
        if self.level >= self.threshold_3 > 0:
            return 3
        if self.level >= self.threshold_2 > 0:
            return 2
        if self.level >= self.threshold_1 > 0:
            return 1
        return 0


class WaterLevelCoordinator(DataUpdateCoordinator[StationData]):
    """Interroga l'API e restituisce i dati della stazione scelta."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL
        )
        self.station_id: str = entry.data[CONF_STATION_ID]
        self._history: deque[tuple[int, float]] = deque(maxlen=20)

    async def _async_update_data(self) -> StationData:
        session = async_get_clientsession(self.hass)
        try:
            stations, data_time = await async_fetch_stations(session)
        except WaterLevelApiError as err:
            raise UpdateFailed(str(err)) from err

        st = next((s for s in stations if s["idstazione"] == self.station_id), None)
        if st is None or st.get("value") is None:
            raise UpdateFailed(f"Stazione {self.station_id} senza dati")

        ts_ms = data_time or int(datetime.now(timezone.utc).timestamp() * 1000)
        measured_at = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        if datetime.now(timezone.utc) - measured_at > STALE_AFTER:
            raise UpdateFailed("Ultima misura troppo vecchia")

        level = float(st["value"])
        if not self._history or self._history[-1][0] != ts_ms:
            self._history.append((ts_ms, level))

        trend = None
        old = next(
            (h for h in self._history if ts_ms - h[0] <= TREND_WINDOW_MS and h[0] < ts_ms),
            None,
        )
        if old:
            trend = round((level - old[1]) / ((ts_ms - old[0]) / 3_600_000), 3)

        return StationData(
            name=st["nomestaz"],
            level=level,
            measured_at=measured_at,
            threshold_1=float(st.get("soglia1") or 0),
            threshold_2=float(st.get("soglia2") or 0),
            threshold_3=float(st.get("soglia3") or 0),
            trend_m_h=trend,
            latitude=_coord(st.get("lat")),
            longitude=_coord(st.get("lon")),
        )


def _coord(raw) -> float | None:
    """Le coordinate dell'API sono gradi * 100000 (es. 1162491 -> 11.62491)."""
    try:
        return round(int(raw) / 100000, 5)
    except (TypeError, ValueError):
        return None
