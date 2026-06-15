# Dictionnaire de données — Airline Performance 2009-2018

## Couche Silver — `stg_flights` + `int_flights_enriched`

| Colonne | Type | Description | Exemple | Notes |
|---|---|---|---|---|
| FL_DATE | Date | Date complète du vol | 2015-06-15 | Source principale temporalité |
| OP_UNIQUE_CARRIER | String | Code IATA carrier (renommé depuis OP_CARRIER) | DL | Clé de jointure dim_carrier |
| OP_CARRIER_FL_NUM | Integer | Numéro de vol | 1234 |  |
| YEAR | Integer | Année extraite depuis FL_DATE | 2015 | Calculé |
| MONTH | Integer | Mois (1-12) | 6 | Clé saisonnalité |
| QUARTER | Integer | Trimestre (1-4) | 2 | Clé analyse fusions |
| DAY_OF_WEEK | Integer | Jour semaine (1=Lundi 7=Dimanche) | 1 | Clé pattern hebdo |
| ORIGIN | String | Code IATA aéroport départ | ATL |  |
| DEST | String | Code IATA aéroport arrivée | JFK |  |
| CRS_DEP_TIME | Integer | Heure départ programmée (HHMM) | 1435 | 1435 = 14h35 |
| DEP_TIME | Float | Heure départ réelle (HHMM) | 1442 | NULL si annulé |
| DEP_DELAY | Float | Retard départ en minutes | 7.0 | Négatif = avance |
| DEP_DEL15 | Integer | Retard départ > 15 min (0/1) | 0 | Calculé depuis DEP_DELAY |
| TAXI_OUT | Float | Roulage avant décollage (min) | 12.0 | Indicateur congestion départ |
| WHEELS_OFF | Float | Heure décollage réel (HHMM) | 1454 |  |
| WHEELS_ON | Float | Heure atterrissage réel (HHMM) | 1623 |  |
| TAXI_IN | Float | Roulage après atterrissage (min) | 5.0 | Indicateur congestion arrivée |
| CRS_ARR_TIME | Integer | Heure arrivée programmée (HHMM) | 1615 |  |
| ARR_TIME | Float | Heure arrivée réelle (HHMM) | 1628 | NULL si annulé |
| ARR_DELAY | Float | Retard arrivée en minutes | 13.0 | METRIQUE PRINCIPALE |
| ARR_DEL15 | Integer | Retard arrivée > 15 min (0/1) | 0 | Calculé — base OTP officiel DOT |
| CANCELLED | Float | Vol annulé (1=oui 0=non) | 0.0 |  |
| CANCELLATION_CODE | String | Cause annulation A/B/C/D | B | A=Carrier B=Météo C=NAS D=Sécu |
| DIVERTED | Float | Vol détourné (1=oui) | 0.0 |  |
| CRS_ELAPSED_TIME | Float | Durée planifiée (min) | 180.0 |  |
| ACTUAL_ELAPSED_TIME | Float | Durée réelle (min) | 194.0 | NULL si annulé |
| AIR_TIME | Float | Temps vol effectif (min) | 177.0 | < ACTUAL_ELAPSED_TIME |
| DISTANCE | Float | Distance vol en miles | 950.0 |  |
| CARRIER_DELAY | Float | Minutes retard imputables carrier | 0.0 | NULL si non retardé |
| WEATHER_DELAY | Float | Minutes retard météo extrême | 0.0 | NULL si non retardé |
| NAS_DELAY | Float | Minutes retard système aviation | 13.0 | NULL si non retardé |
| SECURITY_DELAY | Float | Minutes retard sécurité | 0.0 | NULL si non retardé |
| LATE_AIRCRAFT_DELAY | Float | Minutes retard avion précédent | 0.0 | NULL si non retardé |
| total_delay_causes | Float | Somme 5 causes retard | 13.0 | Calculé — doit = ARR_DELAY |

---

## Couche Gold

### `mart_merger_impact`

| Colonne | Type | Description |
|---|---|---|
| carrier_key | String | Code IATA carrier |
| YEAR | Integer | Année |
| QUARTER | Integer | Trimestre |
| fusion_periode | String | pre / during / post / not_merged |
| carrier_group | String | Groupe post-fusion (ex: United Group) |
| total_flights | Integer | Nombre total de vols |
| otp_pct | Float | % vols arrivés à l'heure (ARR_DEL15=0) |
| avg_arr_delay | Float | Retard moyen sur vols retardés (min) |
| cancellation_rate | Float | % vols annulés |
| min_carrier | Float | Total minutes retard carrier |
| min_late_aircraft | Float | Total minutes retard late aircraft |
| min_nas | Float | Total minutes retard NAS |
| min_weather | Float | Total minutes retard météo |
| min_security | Float | Total minutes retard sécurité |
| pct_carrier | Float | % carrier sur total minutes retard |
| pct_late_aircraft | Float | % late aircraft sur total minutes retard |
| pct_nas | Float | % NAS sur total minutes retard |

### `mart_otp_monthly`

| Colonne | Type | Description |
|---|---|---|
| carrier_key | String | Code IATA carrier |
| YEAR | Integer | Année |
| MONTH | Integer | Mois (1-12) |
| season | String | Saison (Winter/Spring/Summer/Fall) |
| total_flights | Integer | Nombre total de vols |
| otp_pct | Float | OTP mensuel % |
| avg_arr_delay | Float | Retard moyen (min) |
| cancellation_rate | Float | % annulations |
| min_carrier | Float | Minutes retard carrier |
| min_weather | Float | Minutes retard météo |
| min_nas | Float | Minutes retard NAS |
| min_late_aircraft | Float | Minutes retard late aircraft |

### `mart_seasonality`

| Colonne | Type | Description |
|---|---|---|
| MONTH | Integer | Mois (1-12) |
| DAY_OF_WEEK | Integer | Jour semaine (1-7) |
| dep_hour | Float | Heure départ arrondie (0-23) |
| season | String | Saison |
| total_flights | Integer | Nombre de vols |
| otp_pct | Float | OTP % |
| avg_delay_when_late | Float | Retard moyen si retardé (min) |
| pct_weather | Float | % minutes retard météo |
| pct_nas | Float | % minutes retard NAS |
| pct_carrier | Float | % minutes retard carrier |

### `dim_carrier` (seed)

| Colonne | Type | Description |
|---|---|---|
| iata_code | String | Code IATA officiel |
| carrier_name | String | Nom complet de la compagnie |
| carrier_type | String | Legacy / LCC / ULCC / Regional |
| active_from | Integer | Première année active dans le dataset |
| active_to | Integer | Dernière année active dans le dataset |
| merged_into | String | Code IATA du carrier absorbeur (NULL si pas de fusion) |
| carrier_group_post_merger | String | Groupe consolidé post-fusion |
