# Livello Idrometrico Emilia-Romagna (Home Assistant)

Custom integration che legge il livello di un idrometro della rete regionale
(Allerta Meteo Emilia-Romagna / ARPAE) ed espone entità per allarmi e automazioni.

## Installazione
Copia `custom_components/waterlevel` in `<config>/custom_components/`, riavvia
Home Assistant, poi *Impostazioni → Dispositivi e servizi → Aggiungi integrazione →
Livello Idrometrico Emilia-Romagna* e scegli la stazione (default: **Gandazzolo Savena**, id 3150).

## Entità
| Entità | Descrizione |
|---|---|
| `sensor.<stazione>_livello` | Livello in m (quota idrometrica); attributi `threshold_1/2/3` |
| `sensor.<stazione>_tendenza` | Variazione in m/h sugli ultimi ~90 min |
| `sensor.<stazione>_livello_di_allerta` | 0 = nessuna soglia, 1/2/3 = gialla/arancione/rossa |
| `binary_sensor.<stazione>_soglia_N_superata` | `on` se la soglia N è superata |
| `sensor.<stazione>_soglia_N_...` | Valore in m delle soglie 1/2/3 (diagnostica); `unknown` se non definita |
| `sensor.<stazione>_ultima_misura` | Timestamp dell'ultima misura (disabilitato di default) |

Se i dati sono assenti o più vecchi di 3 ore le entità diventano `unavailable`.

## Esempio di automazione
```yaml
automation:
  - alias: "Savena - soglia arancione"
    trigger:
      - platform: state
        entity_id: binary_sensor.gandazzolo_savena_soglia_2_superata_arancione
        to: "on"
    action:
      - service: notify.notify
        data:
          title: "Savena: soglia arancione superata"
          message: "Livello {{ states('sensor.gandazzolo_savena_livello') }} m"
```

## API utilizzata
I dati arrivano dalla mappa "Livello idrometrico" di
[Allerta Meteo Emilia-Romagna](https://allertameteo.regione.emilia-romagna.it/livello-idrometrico)
(Regione Emilia-Romagna / ARPAE). L'API **non è documentata ufficialmente**:
è la stessa chiamata usata dal sito, individuata osservando il traffico di rete della mappa.

**Richiesta**
```
GET https://allertameteo.regione.emilia-romagna.it/o/api/allerta/get-sensor-values-no-time
    ?variabile=254,0,0/1,-,-,-/B13215
    &time=<ms>
    &ts=<ms>
    &latestAvailableTimeIsKnown=false
```

| Parametro | Descrizione |
|---|---|
| `variabile` | Livello idrometrico (codice `B13215`). Valore fisso. |
| `time`, `ts` | Timestamp in millisecondi (epoch) arrotondato per difetto allo slot da 30 minuti. |
| `latestAvailableTimeIsKnown` | `false` |

Non serve autenticazione. Una sola chiamata restituisce **tutte** le stazioni (circa 265).

**Risposta**: array JSON. Il primo elemento contiene il timestamp dell'ultimo dato
disponibile, gli altri sono le stazioni.
```json
[
  { "time": "1794308400000" },
  {
    "idstazione": "3150",
    "nomestaz": "Gandazzolo Savena",
    "value": 8.83,
    "soglia1": 12.5,
    "soglia2": 14,
    "soglia3": 15,
    "precedente": "N",
    "ordinamento": 1049,
    "lon": "1162491",
    "lat": "4467293"
  }
]
```

| Campo | Significato |
|---|---|
| `idstazione` | Identificativo della stazione (usato come scelta nel config flow). |
| `nomestaz` | Nome della stazione. |
| `value` | Livello in metri (quota idrometrica); `null` se non c'è misura per lo slot richiesto. |
| `soglia1/2/3` | Soglie di allerta in metri (gialla, arancione, rossa); `0` se non definite. |
| `lon`, `lat` | Coordinate in metri (proiezione UTM, non usate dall'integrazione). |
| `precedente`, `ordinamento` | Campi interni del sito, non usati. |

**Comportamento dell'integrazione**
- Gli slot sono da 30 minuti; il componente interroga l'API ogni 10 minuti.
- Se lo slot corrente non è ancora popolato (tutti i `value` a `null`), ritenta con i 2 slot precedenti.
- Se i dati mancano o l'ultima misura ha più di 3 ore, le entità diventano `unavailable`.
- Timeout di 20 secondi per richiesta.

**Stazioni sul Savena** (soglie 1 / 2 / 3 lette dall'API):

| Stazione | ID | Soglie (m) |
|---|---|---|
| Gandazzolo Savena | 3150 | 12.5 / 14 / 15 |
| S. Ruffillo Savena | 5524 | 0.8 / 1.2 / 1.5 |
| Loiano Ponte Savena | 3159 | 1 / 1.5 / 2 |

## Note
- L'API usata (`/o/api/allerta/get-sensor-values-no-time`) non è documentata
  ufficialmente e può cambiare. I dati si aggiornano ogni ~30 min.
- Non usare come unico sistema di allarme: segui le allerte ufficiali della Protezione Civile.
