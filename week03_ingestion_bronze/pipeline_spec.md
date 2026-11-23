# Spécification du pipeline `pl_ingest_batch`

## Principe incrémental
Chaque notebook Bronze lit son **watermark** dans `ops_watermarks`, extrait uniquement
la fenêtre `[watermark - 3 h, maintenant]`, écrit en append, puis avance le watermark
**après** l'écriture. Le recouvrement de 3 h rattrape les données tardives ; les doublons
sont éliminés en Silver.

## Activités
1. **Notebook** `nb_bronze_ingest_eco2mix` (paramètre `since_override`, vide par défaut)
2. **Notebook** `nb_bronze_ingest_meteo` (paramètre `since_override`)
3. Les deux en parallèle, puis une activité de succès/échec.

## Paramètres
| Nom | Type | Défaut | Usage |
|---|---|---|---|
| `since_override` | string | vide | Backfill manuel : force une date de départ (ISO 8601) |

## Gestion d'erreurs
- Relance : 3 essais, 60 s d'intervalle sur les notebooks.
- Un échec n'avance jamais le watermark (il est mis à jour seulement après l'écriture).
- En cas d'échec final : alerte (Teams ou email) et écriture dans `ops_pipeline_runs` (semaine 5).

## Planification
Toutes les heures. Désactiver hors des sessions de travail pour économiser la capacité.

## Critères d'acceptation
- [ ] Premier run : charge 30 jours (éco2mix) / 7 jours (météo)
- [ ] Deuxième run immédiat : charge presque rien (seulement la fenêtre de recouvrement)
- [ ] Un run avec `since_override` ancien recharge l'historique sans casser Silver (idempotent)
- [ ] Un échec simulé (mauvaise URL) laisse le watermark inchangé
- [ ] `ops_watermarks` contient une ligne par table Bronze
