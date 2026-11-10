"""Costanti per l'integrazione Livello Idrometrico Emilia-Romagna."""
from datetime import timedelta

DOMAIN = "waterlevel"

API_URL = (
    "https://allertameteo.regione.emilia-romagna.it/o/api/allerta/"
    "get-sensor-values-no-time"
)
# Variabile "livello idrometrico" (B13215) come usata dalla mappa ufficiale
API_VARIABLE = "254,0,0/1,-,-,-/B13215"

CONF_STATION_ID = "station_id"
CONF_STATION_NAME = "station_name"
DEFAULT_STATION_ID = "3150"  # Gandazzolo Savena

SLOT_MS = 30 * 60 * 1000  # i dati sono su slot da 30 minuti
UPDATE_INTERVAL = timedelta(minutes=10)
# Se l'ultima misura e' piu' vecchia di cosi' l'entita' diventa unavailable
STALE_AFTER = timedelta(hours=3)
TREND_WINDOW_MS = 90 * 60 * 1000
