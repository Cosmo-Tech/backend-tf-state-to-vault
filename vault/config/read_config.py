import os
import sys
import json
import logging
import hvac
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class ReadConfig:

    def __init__(self, local_file=None, use_azure=False, version_engine: str = "v2"):
        for v in [
            "VAULT_ADDR",
            "VAULT_TOKEN",
            "TENANT_ID",
            "ORGANIZATION_NAME",
            "PLATFORM_ID",
            "STORAGE_ACCOUNT_NAME",
            "STORAGE_ACCOUNT_KEY",
            "STORAGE_CONTAINER",
            "TFSTATE_BLOB_NAME",
        ]:
            if v not in os.environ:
                logger.error(f" {v} is missing")
                sys.exit(1)

        self.version_engine = version_engine
        self.server_id = os.environ.get("VAULT_ADDR")
        self.token = os.environ.get("VAULT_TOKEN")
        self.org_name = os.environ.get("ORGANIZATION_NAME")
        self.tenant_id = os.environ.get("TENANT_ID")
        self.cluster_name = os.environ.get("CLUSTER_NAME")
        self.platform_id = os.environ.get("PLATFORM_ID")
        self.storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        self.storage_secret = os.environ.get("STORAGE_ACCOUNT_KEY")
        self.storage_container = os.environ.get("STORAGE_CONTAINER")
        self.tfstate_blob_name = os.environ.get("TFSTATE_BLOB_NAME")

        self.prefix = f"{self.tenant_id}/babylon/config/{self.platform_id}"
        self.prefix_client = f"{self.tenant_id}/babylon/{self.platform_id}"
        self.prefix_platform = f"{self.tenant_id}/platform"

        self.vault_prefix = f"{self.tenant_id}/babylon/config/{self.platform_id}"

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
            account_key = (
                f"AccountKey={self.storage_secret};EndpointSuffix=core.windows.net"
            )
            conn_str = f"DefaultEndpointsProtocol=https;AccountName={self.storage_name};{account_key}"
            self.blob_client = BlobServiceClient.from_connection_string(conn_str)
            logger.info("Successfully initialized Azure Blob client")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob client: {str(e)}")
            self.blob_client = None

    def _init_vault(self):
        self.vault_client = hvac.Client(url=self.server_id, token=self.token)

    def _read_config(self, resource: str):
        if self.use_azure:
            return self._read_from_azure(resource)
        else:
            return self._read_from_vault(f"{self.vault_prefix}/{resource}")

    def _read_from_azure(self, resource):
        try:
            if not self.blob_client:
                logger.error("Azure Blob client is not initialized")
                return {}
            container_client = self.blob_client.get_container_client(
                self.storage_container
            )
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
            resource = schema.split("/")[-1]
            if self.version_engine == "v1":
                response = self.vault_client.read(path=schema)
                data = response.get("data")
                output = dict()
                for i, k in data.items():
                    output.setdefault(f"out_{resource}_{i}", dict(value=k))
                return {"outputs": output} if "data" in response else {}
            else:
                response = self.vault_client.secrets.kv.v2.read_secret_version(
                    path=schema, mount_point=self.org_name
                )
                data = response.get("data").get("data")
                output = dict()
                for i, k in data.items():
                    output.setdefault(f"out_{resource}_{i}", dict(value=k))
            return (
                {"outputs": output}
                if "data" in response and "data" in response["data"]
                else {}
            )
        except Exception as e:
            logger.error(f"Failed to read from Vault: {str(e)}")
            return {}

    def get_config(self, resource: str):
        if resource == "acr":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "adt":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "adx":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "app":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "api":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "azure":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "babylon":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "github":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "platform":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "powerbi":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "webapp":
            self._read_config(f"{self.prefix}/{resource}")
        if resource == "":
            logger.error(
                """
The resource should be ['acr', 'adt', 'adx', 'api', 'app', 'azure', 'babylon', 'github', 
'platform', 'powerbi', 'webapp', 'client', 'storage']
"""
            )
            return None

    def read_babylon_client_secret(self):
        return self._read_from_vault(f"{self.prefix_client}/client")

    def read_storage_client_secret(self):
        return self._read_from_vault(
            f"{self.prefix_platform}/{self.platform_id}/storage/account"
        )

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
        data = {resource: self._read_config(resource) for resource in resources}
        data["client"] = self.read_babylon_client_secret()
        data["storage"] = self.read_storage_client_secret()
        return data
