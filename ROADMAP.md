# Feuille de route (10 semaines, ~10 h/semaine)

| Sem. | Dossier | Objectif | Fichiers clés |
|---|---|---|---|
| 1 | `week01_cadrage` | Cadrage, architecture, conventions | architecture.md, naming-conventions.md, backlog.md |
| 2 | `week02_entra_rbac` | Groupes Entra et rôles | rbac-matrix.md, entra_groups.sh |
| 3 | `week03_ingestion_bronze` | Ingestion batch **incrémentale** vers Bronze | watermark_helpers.py, bronze_ingest_eco2mix.py, bronze_ingest_meteo.py, pipeline_spec.md |
| 4 | `week04_silver` | Nettoyage et MERGE incrémental | silver_eco2mix.py, silver_meteo.py, incremental_strategy.md |
| 5 | `week05_qualite_logs` | Qualité et journalisation | quality_checks.py, logging_helpers.py, create_log_tables.sql |
| 6 | `week06_gold` | Modèle en étoile, faits incrémentaux | gold_dimensions.sql, gold_facts.py |
| 7 | `week07_temps_reel` | Eventstream, KQL, alertes | sensor_simulator.py, kql_queries.kql, activator_rules.md |
| 8 | `week08_bi_securite` | Sémantique, RLS, rapport | semantic_model.md, rls_roles.md, report_spec.md |
| 9 | `week09_cicd` | Git, déploiement multi-env | ci.yml, deploy.yml, deploy_fabric.py |
| 10 | `week10_gouvernance_finition` | Lineage, monitoring, démo | observability.md, lineage_checklist.md, demo_script.md |

## Règle de fin de semaine

Chaque semaine se termine par : commit propre, README à jour, capture d'écran dans `docs/`, 3 lignes dans `CHANGELOG.md`.
