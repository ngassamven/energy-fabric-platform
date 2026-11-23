#!/usr/bin/env bash
# Création des groupes Entra et du service principal via Azure CLI.
# Prérequis : az login (compte avec droits sur le répertoire Entra).
set -euo pipefail

for g in admins engineers analysts viewers; do
  name="grp-energy-${g}"
  az ad group create --display-name "$name" --mail-nickname "$name" \
    --description "Energy Fabric platform - ${g}"
done

# Service principal pour le déploiement
az ad sp create-for-rbac --name sp-energy-deploy --skip-assignment

# Ajouter un utilisateur à un groupe (exemple) :
# az ad group member add --group grp-energy-engineers --member-id <objectId>
echo "Groupes et service principal créés. Note les identifiants dans un gestionnaire de secrets."
