import os
import sys
import json
import logging
import hvac
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class ReadConfig:

    def __init__(self, local_file=None, use_azure=False):
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

        self.vault_prefix = f"{self.tenant_id}/babylon/config/{self.platform_name}"

        self.local_file = local_file
        self.use_azure = use_azure and not local_file
        self.data = None

        self.vault_client = None
        self.blob_client = None

        if self.local_file:
            self._read_local_state()
        elif self.use_azure:
            self._init_azure()
        else:
            self._init_vault()

    def _read_local_state(self):
        logger.info(f"Attempting to read from local file: {self.local_file}")
        try:
            with open(self.local_file, "r") as f:
                self.data = json.load(f)
            logger.info(f"Successfully read data from {self.local_file}")
        except Exception as e:
            logger.error(f"Failed to read from local file: {str(e)}")
            self.data = {}

    def _init_azure(self):
        try:
            account_key = (f"AccountKey={self.storage_secret};EndpointSuffix=core.windows.net")
            conn_str = f"DefaultEndpointsProtocol=https;AccountName={self.storage_name};{account_key}"
            self.blob_client = BlobServiceClient.from_connection_string(conn_str)
            logger.info("Successfully initialized Azure Blob client")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob client: {str(e)}")
            self.blob_client = None

    def _init_vault(self):
        self.vault_client = hvac.Client(url=self.server_id, token=self.token)

    def _read_config(self, resource: str):
        if self.local_file:
            return self.data.get("outputs", {}).get(resource, {}).get("value", {})
        elif self.use_azure:
            return self._read_from_azure(resource)
        else:
            return self._read_from_vault(f"{self.vault_prefix}/{resource}")

    def _read_from_azure(self, resource):
        try:
            if not self.blob_client:
                logger.error("Azure Blob client is not initialized")
                return {}
            container_client = self.blob_client.get_container_client(self.storage_container)
            blob_client = container_client.get_blob_client(self.tfstate_blob_name)
            blob_data = blob_client.download_blob().readall()
            if not blob_data:
                logger.warning(f"No data found in Azure Blob for resource: {resource}")
                return {}
            data = json.loads(blob_data)
            return data.get("outputs", {}).get(resource, {}).get("value", {})
        except Exception as e:
            logger.error(f"Failed to read from Azure: {str(e)}")
            return {}

    def _read_from_vault(self, schema):
        try:
            response = self.vault_client.secrets.kv.v2.read_secret_version(path=schema, mount_point=self.org_name)
            return (response["data"]["data"] if "data" in response and "data" in response["data"] else {})
        except Exception as e:
            logger.error(f"Failed to read from Vault: {str(e)}")
            return {}

    def get_config(self, resource: str):
        match resource:
            case ("acr"
                  | "adt"
                  | "adx"
                  | "app"
                  | "api"
                  | "azure"
                  | "babylon"
                  | "github"
                  | "platform"
                  | "powerbi"
                  | "webapp"):
                return self._read_config(resource)
            case "client":
                return self._read_config("client")
            case "storage":
                return self._read_config("storage/account")
            case _:
                logger.error("""
The resource should be ['acr', 'adt', 'adx', 'api', 'app', 'azure', 'babylon', 'github', 
'platform', 'powerbi', 'webapp', 'client', 'storage']
""")
                return None

    def read_babylon_client_secret(self):
        return self._read_config(f"{self.prefix_client}/client")

    def read_storage_client_secret(self):
        return self._read_config(f"{self.prefix_platform}/{self.platform_name}/storage/account")

    def read_acr(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_adt(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_app(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_adx(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_api(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_azure(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_babylon(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_github(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_platform(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_powerbi(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_webapp(self, resource):
        return self._read_config(f"{self.prefix}/{resource}")

    def read_all_config(self):
        logger.info("Reading all config")
        resources = [
            "acr",
            "adt",
            "adx",
            "app",
            "api",
            "azure",
            "babylon",
            "github",
            "platform",
            "powerbi",
            "webapp",
        ]
        return {resource: self._read_config(resource) for resource in resources}
