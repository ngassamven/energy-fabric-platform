# Observabilité

## Outils
| Besoin | Outil |
|---|---|
| Suivre les exécutions | Monitoring hub |
| Analyser l'activité en détail | Workspace monitoring (Eventhouse du workspace) |
| Alertes sur échec | Alertes de pipeline (Teams/email) ou Activator |
| Traçabilité métier | tables `ops_pipeline_runs` et `ops_quality_results` |

## Indicateurs à suivre
- Taux de succès des pipelines (7 derniers jours)
- Durée moyenne des runs
- Lignes rejetées par jour
- Fraîcheur des données Silver et Gold

## À livrer
- Capture du Monitoring hub avec des runs réussis et un échec
- Requête KQL sur Workspace monitoring (si activé) sauvegardée dans `docs/`
