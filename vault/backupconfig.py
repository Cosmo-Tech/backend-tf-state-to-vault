import logging
import sys
import os
import json
import pathlib
from hvac import Client
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class BackupConfig:
    def __init__(self):
        for v in [
            "VAULT_ADDR",
            "VAULT_TOKEN",
            "ORGANIZATION_NAME",
            "TENANT_ID",
            "CLUSTER_NAME",
            "PLATFORM_NAME",
            "STORAGE_ACCOUNT_NAME",
            "STORAGE_ACCOUNT_KEY",
            "STORAGE_CONTAINER",
            "TFSTATE_BLOB_NAME",
        ]:
            if v not in os.environ:
                logger.error(f" {v} is missing")
                sys.exit(1)

        self.server_id = os.environ.get("VAULT_ADDR")
        self.token = os.environ.get("VAULT_TOKEN")
        self.org_name = os.environ.get("ORGANIZATION_NAME")
        self.tenant_id = os.environ.get("TENANT_ID")
        self.cluster_name = os.environ.get("CLUSTER_NAME")
        self.platform_name = os.environ.get("PLATFORM_NAME")
        self.storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        self.storage_secret = os.environ.get("STORAGE_ACCOUNT_KEY")
        self.storage_container = os.environ.get("STORAGE_CONTAINER")
        self.tfstate_blob_name = os.environ.get("TFSTATE_BLOB_NAME")

        org_tenant = f"{self.org_name}/{self.tenant_id}"
        self.prefix = f"{org_tenant}/babylon/config"

    def backup_config(self):
        client = Client(url=self.server_id, token=self.token)
        acr_path = f"{self.prefix}/{self.platform_name}/acr"
        adt_path = f"{self.prefix}/{self.platform_name}/adt"
        adx_path = f"{self.prefix}/{self.platform_name}/adx"
        api_path = f"{self.prefix}/{self.platform_name}/api"
        app_path = f"{self.prefix}/{self.platform_name}/app"
        azure_path = f"{self.prefix}/{self.platform_name}/azure"
        babylon_path = f"{self.prefix}/{self.platform_name}/babylon"
        github_path = f"{self.prefix}/{self.platform_name}/github"
        platform_path = f"{self.prefix}/{self.platform_name}/platform"
        powerbi_path = f"{self.prefix}/{self.platform_name}/powerbi"
        webapp_path = f"{self.prefix}/{self.platform_name}/webapp"

        acr = client.read(acr_path).get('data', {})
        adt = client.read(adt_path).get('data', {})
        adx = client.read(adx_path).get('data', {})
        api = client.read(api_path).get('data', {})
        app = client.read(app_path).get('data', {})
        azure = client.read(azure_path).get('data', {})
        babylon = client.read(babylon_path).get('data', {})
        github = client.read(github_path).get('data', {})
        platform = client.read(platform_path).get('data', {})
        powerbi = client.read(powerbi_path).get('data', {})
        webapp = client.read(webapp_path).get('data', {})

        config = {
            "acr": acr,
            "adt": adt,
            "adx": adx,
            "api": api,
            "app": app,
            "azure": azure,
            "babylon": babylon,
            "github": github,
            "platform": platform,
            "powerbi": powerbi,
            "webapp": webapp
        }
        output_file = f"backup-{self.platform_name}.json"
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration sauvegardée dans {output_file}")

    def save_backup_to_blob(self):
        _file = pathlib.Path(f"backup-{self.platform_name}.json")
        prefix = "DefaultEndpointsProtocol=https;"
        prefix += f"AccountName={self.storage_name}"
        conn_str = f"{prefix};AccountKey={self.storage_secret};"
        conn_str += "EndpointSuffix=core.windows.net"
        self.blob_client = BlobServiceClient.from_connection_string(conn_str)
        try:
            service = self.blob_client.get_container_client(
                container=self.storage_container
            )
            blob = service.get_blob_client(blob=self.tfstate_blob_name)
            with open(_file, 'rb') as data:
                blob.upload_blob(data, overwrite=True)
            logger.info(f"Backup file uploaded to {self.tfstate_blob_name}")
        except Exception as e:
            logger.error(f"Error uploading backup file: {e}")
            sys.exit(1)