# Sécurité au niveau des lignes (RLS)

Les données éco2mix sont nationales : pour démontrer le RLS, on l'applique sur la **dimension ville** (météo).

## Rôles
| Rôle | Filtre DAX sur `dim_city` | Groupe Entra |
|---|---|---|
| `RLS_Paris` | `[city] = "paris"` | `grp-energy-analysts` (test) |
| `RLS_All` | aucun filtre | `grp-energy-engineers` |

## Test
1. Dans Power BI Desktop ou le service : « Afficher en tant que » le rôle `RLS_Paris`.
2. Vérifier que seules les données de Paris apparaissent.
3. Faire une capture dans `docs/`.

## Rappels
- Le RLS ne s'applique pas aux rôles Admin, Member et Contributor du workspace : teste avec un compte Viewer.
- Documente la limite dans le README.
