"""Config flow: scelta della stazione idrometrica."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import WaterLevelApiError, async_fetch_stations
from .const import CONF_STATION_ID, CONF_STATION_NAME, DEFAULT_STATION_ID, DOMAIN


class WaterLevelConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._stations: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if not self._stations:
            try:
                stations, _ = await async_fetch_stations(
                    async_get_clientsession(self.hass)
                )
            except WaterLevelApiError:
                errors["base"] = "cannot_connect"
            else:
                self._stations = {
                    s["idstazione"]: s["nomestaz"]
                    for s in sorted(stations, key=lambda s: s["nomestaz"])
                }

        if user_input is not None and not errors:
            sid = user_input[CONF_STATION_ID]
            await self.async_set_unique_id(sid)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._stations[sid],
                data={CONF_STATION_ID: sid, CONF_STATION_NAME: self._stations[sid]},
            )

        options = [
            SelectOptionDict(value=i, label=n) for i, n in self._stations.items()
        ]
        default = DEFAULT_STATION_ID if DEFAULT_STATION_ID in self._stations else vol.UNDEFINED
        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_ID, default=default): SelectSelector(
                    SelectSelectorConfig(
                        options=options, mode=SelectSelectorMode.DROPDOWN, sort=True
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
