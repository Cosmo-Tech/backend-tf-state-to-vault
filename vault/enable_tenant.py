import logging
import sys
import os
from hvac import Client
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")

class EnableNewTenant:
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
    
    def enable_tenant(self):
        client = Client(url=self.server_id, token=self.token)
        client.sys.enable_secrets_engine(backend_type='kv', path=self.org_name, options={'version': '1'})
        client.sys.enable_secrets_engine(backend_type='kv', path='organization', options={'version': '1'})
        data = {
            "tenant": self.tenant_id,
        }
        client.write(f"organization/{self.org_name}", **data)
        client.sys.enable_auth_method(method_type='userpass', path=f'userpass-{self.org_name}')