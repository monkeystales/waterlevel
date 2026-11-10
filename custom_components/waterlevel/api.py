"""Client per l'API (non ufficiale) di Allerta Meteo Emilia-Romagna."""
from __future__ import annotations

import time
from typing import Any

import aiohttp

from .const import API_URL, API_VARIABLE, SLOT_MS


class WaterLevelApiError(Exception):
    """Errore di comunicazione con l'API."""


async def async_fetch_stations(
    session: aiohttp.ClientSession, slots_back: int = 3
) -> tuple[list[dict[str, Any]], int | None]:
    """Scarica tutte le stazioni idrometriche.

    Ritorna (stazioni, timestamp_ms_ultimo_dato). Se lo slot corrente non e'
    ancora popolato, prova gli slot precedenti.
    """
    now_slot = int(time.time() * 1000) // SLOT_MS * SLOT_MS
    last_error: Exception | None = None
    for i in range(slots_back):
        t = now_slot - i * SLOT_MS
        params = {
            "variabile": API_VARIABLE,
            "time": t,
            "ts": t,
            "latestAvailableTimeIsKnown": "false",
        }
        try:
            async with session.get(
                API_URL, params=params, timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            last_error = err
            continue

        if not isinstance(data, list):
            last_error = WaterLevelApiError("Risposta inattesa")
            continue

        stations = [d for d in data if "idstazione" in d]
        data_time = next(
            (int(d["time"]) for d in data if "time" in d and "idstazione" not in d),
            None,
        )
        if any(s.get("value") is not None for s in stations):
            return stations, data_time

    raise WaterLevelApiError(f"Nessun dato disponibile: {last_error}")
