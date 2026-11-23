# Architecture (Semaine 1)

## Objectif métier
Suivre le mix électrique français, la part de renouvelable, le taux de CO2 et l'effet de la météo sur la consommation.

## Questions auxquelles le rapport répond
1. Quelle est la part de chaque source (nucléaire, éolien, solaire, hydraulique, gaz...) par jour ?
2. Quelle est l'évolution du taux de CO2 ?
3. Comment la température influence la consommation ?
4. Y a-t-il des anomalies (données manquantes, pics) ?

## Sources
| Source | Mode | Fréquence | Remarque |
|---|---|---|---|
| ODRE / RTE éco2mix national temps réel | API REST | 15 min (batch toutes les heures) | vérifier les noms de colonnes |
| Open-Meteo | API REST | horaire | gratuite, sans clé |
| Capteurs simulés | Eventstream | secondes | script Python |

## Couches
- **Bronze** : données brutes + colonnes techniques (`_ingested_at`, `_source`, `_batch_id`). Jamais modifiées.
- **Silver** : typage, dédoublonnage, contrôles qualité, rejets isolés.
- **Gold** : modèle en étoile pour la BI.

## Stratégie d'ingestion : incrémentale par watermark
Chaque couche ne traite que les nouvelles données, repérées par un watermark stocké dans `ops_watermarks`.
Détail dans `week04_silver/incremental_strategy.md`.

| Couche | Watermark | Écriture |
|---|---|---|
| Bronze | dernière `date_heure` / `time` chargée (recouvrement de 3 h) | append |
| Silver | dernier `_ingested_at` traité | MERGE sur la clé |
| Gold | dernier `_ingested_at` traité par source Silver | MERGE sur les heures touchées |

## À décider et documenter (ADR)
- Gold dans un Lakehouse ou un Warehouse ? **Choix proposé : Lakehouse** (les scripts de la semaine 6 le supposent). Justifie en 2 lignes.
- Partitionnement des tables : proposé par date pour les faits volumineux ; inutile à ce volume, à justifier.
- Fenêtre de recouvrement (3 h) : à confirmer en observant les retards réels de l'API.

## Schéma
`docs/architecture.png` (source modifiable : `docs/architecture.svg`).
