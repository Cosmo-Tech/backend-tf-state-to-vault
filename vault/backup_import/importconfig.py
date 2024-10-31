import logging
import sys
import os
import json
import pathlib
import hvac
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class ImportConfig:

    def __init__(self):
        for v in [
                "VAULT_ADDR",
                "VAULT_TOKEN",
                "ORGANIZATION_NAME",
                "TENANT_ID",
                "PLATFORM_ID",
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
        self.platform_name = os.environ.get("PLATFORM_ID")
        self.storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        self.storage_secret = os.environ.get("STORAGE_ACCOUNT_KEY")
        self.storage_container = os.environ.get("STORAGE_CONTAINER")
        self.tfstate_blob_name = os.environ.get("TFSTATE_BLOB_NAME")

        tenant = f"{self.tenant_id}"
        self.prefix = f"{tenant}/babylon/config"
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
            service = self.blob_client.get_container_client(container=self.storage_container)
            blob = service.get_blob_client(blob=self.tfstate_blob_name)
            state = blob.download_blob(encoding="utf-8").content_as_bytes()
            self.state = state
        except Exception:
            self.state = "{}"
            logger.info("blob not found")

    def import_config(self, platform_id_to, backup_file):
        client = hvac.Client(url=self.server_id, token=self.token)
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

        if not os.path.exists(backup_file):
            print(f"Backup file {backup_file} does not exist.")
        else:
            with open(backup_file, 'r') as f:
                config = json.load(f)

            # Use the version 2 secrets engine API
            if 'acr' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=acr_path,
                    secret=config['acr'],
                    mount_point=self.org_name,
                )
            if 'adt' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=adt_path,
                    secret=config['adt'],
                    mount_point=self.org_name,
                )
            if 'adx' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=adx_path,
                    secret=config['adx'],
                    mount_point=self.org_name,
                )
            if 'api' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=api_path,
                    secret=config['api'],
                    mount_point=self.org_name,
                )
            if 'app' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=app_path,
                    secret=config['app'],
                    mount_point=self.org_name,
                )
            if 'azure' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=azure_path,
                    secret=config['azure'],
                    mount_point=self.org_name,
                )
            if 'babylon' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=babylon_path,
                    secret=config['babylon'],
                    mount_point=self.org_name,
                )
            if 'github' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=github_path,
                    secret=config['github'],
                    mount_point=self.org_name,
                )
            if 'platform' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=platform_path,
                    secret=config['platform'],
                    mount_point=self.org_name,
                )
            if 'powerbi' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=powerbi_path,
                    secret=config['powerbi'],
                    mount_point=self.org_name,
                )
            if 'webapp' in config:
                client.secrets.kv.v2.create_or_update_secret(
                    path=webapp_path,
                    secret=config['webapp'],
                    mount_point=self.org_name,
                )

            print(f"Configuration restored from {backup_file}")
