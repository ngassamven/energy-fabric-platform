"""Déploiement vers un workspace Fabric avec la bibliothèque fabric-cicd.
Les noms de paramètres peuvent évoluer : vérifie la documentation de fabric-cicd avant usage.
"""
import os
from azure.identity import ClientSecretCredential
from fabric_cicd import FabricWorkspace, publish_all_items

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"],
)

workspace = FabricWorkspace(
    workspace_id=os.environ["WORKSPACE_ID"],
    environment=os.environ["ENVIRONMENT"],
    repository_directory="fabric",  # dossier synchronisé avec Git
    item_type_in_scope=["Notebook", "DataPipeline", "SemanticModel", "Report"],
    token_credential=credential,
)

publish_all_items(workspace)
print("Déploiement terminé")
