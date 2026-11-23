# Règles Data Activator

| Règle | Condition | Action |
|---|---|---|
| Pic de puissance | `power_mw` > seuil (ex. 3 × la moyenne du site) | Message Teams ou email |
| Capteur muet | Aucune mesure depuis 5 min pour un `site` | Message Teams ou email |

## Mise en place
1. Dans l'Eventstream, ajouter la destination Activator (ou créer l'objet depuis l'Eventhouse).
2. Objet = `site`, propriété = `power_mw`.
3. Définir les conditions ci-dessus et l'action.
4. Lancer le simulateur, vérifier le déclenchement (2 % d'anomalies injectées) et faire une capture dans `docs/`.

## Critères d'acceptation
- [ ] Les mesures arrivent dans l'Eventhouse
- [ ] Une anomalie déclenche une alerte reçue
- [ ] Arrêter le simulateur 5 min déclenche l'alerte « capteur muet »
