import os
import sys
import logging
import hvac
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class ReadConfig:
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
        self.prefix = f"{org_tenant}/babylon/config/{self.platform_name}"
        self.prefix_client = f"{org_tenant}/babylon/{self.platform_name}"
        self.prefix_platform = f"{org_tenant}/platform"
    
    def read_config(self, schema: str):
        client = hvac.Client(url=self.server_id, token=self.token)
        data = client.read(schema).get('data', {})
        print(data)
    
    def write_config(self, schema: str):
        client = hvac.Client(url=self.server_id, token=self.token)
        response = client.secrets.kv.v2.read_secret_version(path=schema)
        data = response['data']['data'] if 'data' in response and 'data' in response['data'] else {}
        print(data)
        return data

    def get_config(self, resource: str):
        match resource:
            case "acr":
                self.read_acr(resource)
            case "adt":
                self.read_adt(resource)
            case "adx":
                self.read_adx(resource)
            case "app":
                self.read_app(resource)
            case "api":
                self.read_api(resource)
            case "azure":
                self.read_azure(resource)
            case "babylon":
                self.read_babylon(resource)
            case "github":
                self.read_github(resource)
            case "platform":
                self.read_platform(resource)
            case "powerbi":
                self.read_powerbi(resource)
            case "webapp":
                self.read_webapp(resource)
            case "client":
                self.read_babylon_client_secret()
            case "storage":
                self.read_storage_client_secret()
            case _:
                logger.error(f"The ressource should be ['acr', 'adt', 'adx', 'api', 'app', 'azure', 'babylon', 'github', 'platform', 'powerbi', 'webapp', 'client', 'storage']")
    
    def read_babylon_client_secret(self):
        self.read_config(f"{self.prefix_client}/client")
        return self

    def read_storage_client_secret(self):
        self.read_config(
            f"{self.prefix_platform}/{self.platform_name}/storage/account",
        )
        return self

    def read_acr(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_adt(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_app(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_adx(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_api(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_azure(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_babylon(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_github(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_platform(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_powerbi(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
        return self

    def read_webapp(self, resource):
        self.read_config(f"{self.prefix}/{resource}")
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