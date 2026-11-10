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

## Note
- L'API usata (`/o/api/allerta/get-sensor-values-no-time`) non è documentata
  ufficialmente e può cambiare. I dati si aggiornano ogni ~30 min.
- Non usare come unico sistema di allarme: segui le allerte ufficiali della Protezione Civile.
