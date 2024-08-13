import os
import sys
import logging
from hvac import Client
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class DeletConfig:
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
        self.prefix_client = f"{org_tenant}/babylon/{self.platform_name}"
        self.prefix_platform = f"{org_tenant}/platform"
    
    def delete_config(self, schema: str):
        client = Client(url=self.server_id, token=self.token)
        client.delete(schema)
        return self
    
    def delete_babylon_client_secret(self):
        self.delete_config(f"{self.prefix_client}/client")
        return self

    def delete_storage_client_secret(self):
        self.delete_config(
            f"{self.prefix_platform}/{self.platform_name}/storage/account",
        )
        return self

    def delete_acr(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/acr")
        return self

    def delete_adt(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/adt")
        return self

    def delete_app(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/app")
        return self

    def delete_adx(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/adx")
        return self

    def delete_api(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/api")
        return self

    def delete_azure(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/azure")
        return self

    def delete_babylon(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/babylon")
        return self

    def delete_github(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/github")
        return self

    def delete_plaftorm(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/platform")
        return self

    def delete_powerbi(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/powerbi")
        return self

    def delete_webapp(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/webapp")
        return self
    
    def delete_all_config(self, platform_id):
        self.delete_acr(platform_id)
        self.delete_adt(platform_id)
        self.delete_app(platform_id)
        self.delete_adx(platform_id)
        self.delete_api(platform_id)
        self.delete_azure(platform_id)
        self.delete_babylon(platform_id)
        self.delete_github(platform_id)
        self.delete_plaftorm(platform_id)
        self.delete_powerbi(platform_id)
        self.delete_webapp(platform_id)
        return self
