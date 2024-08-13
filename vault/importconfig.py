import logging
import sys
import os
import json
import pathlib
from hvac import Client
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class ImportConfig:
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
        self.data = None
        self.state = None
        _file = pathlib.Path(f"backup-{self.platform_name}.json")
        if _file.exists():
            with open(_file) as f:
                self.data = json.loads(f.read())
        else:
            self.dowload_ftstate()
            self.data = json.loads(self.state)

        if self.data is None:
            logger.error("data is missing")
            sys.exit(1)
    
    def dowload_ftstate(self):
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
            state = blob.download_blob(encoding="utf-8").content_as_bytes()
            self.state = state
        except Exception:
            self.state = "{}" 
            logger.info("blob not found")

    def import_config(self, platform_id_to):
        client = Client(url=self.server_id, token=self.token)
        acr_path = f"{self.prefix}/{platform_id_to}/acr"
        adt_path = f"{self.prefix}/{platform_id_to}/adt"
        adx_path = f"{self.prefix}/{platform_id_to}/adx"
        api_path = f"{self.prefix}/{platform_id_to}/api"
        app_path = f"{self.prefix}/{platform_id_to}/app"
        azure_path = f"{self.prefix}/{platform_id_to}/azure"
        babylon_path = f"{self.prefix}/{platform_id_to}/babylon"
        github_path = f"{self.prefix}/{platform_id_to}/github"
        platform_path = f"{self.prefix}/{platform_id_to}/platform"
        powerbi_path = f"{self.prefix}/{platform_id_to}/powerbi"
        webapp_path = f"{self.prefix}/{platform_id_to}/webapp"

        input_file = f"backup-{self.platform_name}.json"
        with open(input_file, 'r') as f:
            config = json.load(f)

        client.write(acr_path, **config['acr'])
        client.write(adt_path, **config['adt'])
        client.write(adx_path, **config['adx'])
        client.write(api_path, **config['api'])
        client.write(app_path, **config['app'])
        client.write(azure_path, **config['azure'])
        client.write(babylon_path, **config['babylon'])
        client.write(github_path, **config['github'])
        client.write(platform_path, **config['platform'])
        client.write(powerbi_path, **config['powerbi'])
        client.write(webapp_path, **config['webapp'])
        logger.info(f"Configuration restaurée à partir de {input_file}")