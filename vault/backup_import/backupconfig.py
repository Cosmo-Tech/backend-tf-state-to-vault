import logging
import sys
import os
import json
import hvac

logger = logging.getLogger("Babylon")


class Backup:

    def __init__(self, version_engine: str = "v2"):
        for v in [
                "VAULT_ADDR",
                "VAULT_TOKEN",
                "ORGANIZATION_NAME",
                "TENANT_ID",
                "CLUSTER_NAME",
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
        self.storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        self.storage_secret = os.environ.get("STORAGE_ACCOUNT_KEY")
        self.storage_container = os.environ.get("STORAGE_CONTAINER")
        self.tfstate_blob_name = os.environ.get("TFSTATE_BLOB_NAME")

        self.org_tenant = f"{self.tenant_id}"
        self.prefix = f"{self.org_tenant}/babylon/config"

    def backup_config(self, platform_id: str):
        client = hvac.Client(url=self.server_id, token=self.token)
        self.platform_prefix = f"{self.org_tenant}/platform/{platform_id}"
        self.babylon_prefix = f"{self.org_tenant}/babylon/{platform_id}"

        # Define the paths for KV version 2
        paths = {
            "acr": f"{self.prefix}/{platform_id}/acr",
            "adt": f"{self.prefix}/{platform_id}/adt",
            "adx": f"{self.prefix}/{platform_id}/adx",
            "api": f"{self.prefix}/{platform_id}/api",
            "app": f"{self.prefix}/{platform_id}/app",
            "azure": f"{self.prefix}/{platform_id}/azure",
            "babylon": f"{self.prefix}/{platform_id}/babylon",
            "github": f"{self.prefix}/{platform_id}/github",
            "platform": f"{self.prefix}/{platform_id}/platform",
            "powerbi": f"{self.prefix}/{platform_id}/powerbi",
            "webapp": f"{self.prefix}/{platform_id}/webapp",
            "client": f"{self.babylon_prefix}/client",
            "storage": f"{self.platform_prefix}/storage/account"
        }

        config = {}

        # Read each path using KV version 2
        for k_, schema in paths.items():
            try:
                resource = schema.split("/")[-1]
                if self.version_engine == "v1":
                    response = client.read(path=f"{self.org_name}/{schema}")
                    data = response.get('data', {})
                    output = dict(outputs=dict())
                    for i, k in data.items():
                        output["outputs"].setdefault(f"out_{resource}_{i}", dict(value=k))
                else:
                    response = client.secrets.kv.v2.read_secret_version(
                        path=schema,
                        mount_point=self.org_name,
                    )
                    # config[key] = response.get('data', {}).get('data', {})
            except Exception as e:
                logger.warning(f"Failed to read secret from path '{schema}': {e}")
                # config[key] = {}

            config[k_] = output

        config = {"outputs": config}
        output_file = f"backup.{platform_id}.json"
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration backed up to {output_file}")

    # def save_backup_to_blob(self):
    #     _file = pathlib.Path(f"backup-{self.platform_name}.json")
    #     prefix = "DefaultEndpointsProtocol=https;"
    #     prefix += f"AccountName={self.storage_name}"
    #     conn_str = f"{prefix};AccountKey={self.storage_secret};"
    #     conn_str += "EndpointSuffix=core.windows.net"
    #     self.blob_client = BlobServiceClient.from_connection_string(conn_str)
    #     try:
    #         service = self.blob_client.get_container_client(
    #             container=self.storage_container
    #         )
    #         blob = service.get_blob_client(blob=self.tfstate_blob_name)
    #         with open(_file, 'rb') as data:
    #             blob.upload_blob(data, overwrite=True)
    #         logger.info(f"Backup file uploaded to {self.tfstate_blob_name}")
    #     except Exception as e:
    #         logger.error(f"Error uploading backup file: {e}")
    #         sys.exit(1)
