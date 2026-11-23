# Stratégie incrémentale (Bronze -> Silver -> Gold)

## Le schéma en une phrase
Chaque couche ne traite que ce que la couche précédente a reçu **depuis son dernier passage**,
mesuré par un watermark stocké dans `ops_watermarks`.

| Couche | Watermark basé sur | Lecture | Écriture |
|---|---|---|---|
| Bronze éco2mix | `date_heure` max chargée | API : fenêtre `[wm - 3 h, now]` | append |
| Bronze météo | `time` max chargée | API : fenêtre `[wm - 3 h, now]` | append |
| Silver | `_ingested_at` max traité | Bronze : lignes `> wm` et `<= borne haute` | MERGE sur la clé |
| Gold | `_ingested_at` max traité (par source Silver) | Silver : heures touchées uniquement | MERGE sur (heure, clé) |

## Règles
1. **Le watermark avance en dernier**, après l'écriture réussie : un échec ne perd jamais de données (au pire, on relit).
2. **Borne haute figée** en début de run : un lot qui arrive pendant le run sera traité au suivant.
3. **Recouvrement de 3 h** en Bronze pour les données tardives ; les doublons sont éliminés en Silver.
4. **MERGE conditionnel** (`s._ingested_at > t._ingested_at`) : rejouer un lot ancien n'écrase pas une donnée plus récente.
5. **Backfill** : paramètre `since_override` en Bronze, ou remise à zéro de la ligne du watermark pour retraiter une couche.

## Tests à faire (preuves pour le README)
| Test | Résultat attendu |
|---|---|
| Lancer le pipeline deux fois de suite | Le 2e run écrit très peu (recouvrement) et ne crée aucun doublon en Silver |
| `SELECT date_heure, COUNT(*) FROM silver_eco2mix GROUP BY 1 HAVING COUNT(*) > 1` | 0 ligne |
| Couper le notebook Bronze en cours de route | Watermark inchangé, le run suivant rattrape tout |
| `since_override` = il y a 10 jours | Silver et Gold corrigés, aucun doublon |
| Compter les lignes lues par Silver au run n°2 | Proche de 0 (et non la table entière) |

## Pour réinitialiser une couche
```sql
DELETE FROM ops_watermarks WHERE table_name = 'silver_eco2mix';
```
Le prochain run Silver retraite tout Bronze (le MERGE rend l'opération sans danger).
