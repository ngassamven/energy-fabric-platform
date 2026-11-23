# Matrice RBAC

## Groupes Entra

| Groupe | Contenu | Membres (exemple) |
|---|---|---|
| `grp-energy-admins` | Administration des workspaces | toi |
| `grp-energy-engineers` | Développement data | toi, compte de test 1 |
| `grp-energy-analysts` | Construction de rapports | compte de test 2 |
| `grp-energy-viewers` | Lecture seule | compte de test 3 |

## Rôles de workspace Fabric

| Groupe | Dev | Test | Prod |
|---|---|---|---|
| `grp-energy-admins` | Admin | Admin | Admin |
| `grp-energy-engineers` | Contributor | Contributor | Viewer |
| `grp-energy-analysts` | Viewer | Viewer | Viewer |
| `grp-energy-viewers` | – | – | Viewer |

Principe : **aucun accès attribué à un compte individuel**. Prod modifiée uniquement par le pipeline de déploiement (service principal).

## Service principal
- `sp-energy-deploy` : utilisé par GitHub Actions, rôle Contributor sur Test et Prod.
- Les secrets sont stockés dans les secrets GitHub, jamais dans le code.

## À vérifier dans ton tenant
- Autorisation des service principals dans les paramètres admin Fabric (nécessite un administrateur du tenant).
- Si tu n'as pas les droits Entra sur ton tenant, crée un tenant de développeur Microsoft 365.
