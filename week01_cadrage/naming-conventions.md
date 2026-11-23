# Conventions de nommage

| Objet | Convention | Exemple |
|---|---|---|
| Workspace | `ws-energy-<env>` | `ws-energy-dev` |
| Lakehouse | `lh_<couche>` | `lh_bronze`, `lh_silver`, `lh_gold` |
| Tables | `<couche>_<source>_<entité>` en snake_case | `bronze_rte_eco2mix`, `silver_meteo_hourly` |
| Notebooks | `nb_<couche>_<source>` | `nb_silver_eco2mix` |
| Pipelines | `pl_<action>_<source>` | `pl_ingest_eco2mix` |
| Colonnes techniques | préfixe `_` | `_ingested_at`, `_batch_id`, `_source` |
| Groupes Entra | `grp-energy-<rôle>` | `grp-energy-engineers` |
| Branches Git | `dev`, `test`, `main`, features en `feat/<sujet>` | `feat/silver-eco2mix` |
| Commits | Conventional Commits | `feat: add silver eco2mix merge` |
