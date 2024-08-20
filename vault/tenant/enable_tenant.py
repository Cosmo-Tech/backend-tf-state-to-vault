import logging
import sys
import os
import hvac
from azure.storage.blob import BlobServiceClient
from hvac.exceptions import InvalidPath, InvalidRequest

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
    
    def check_and_enable_secrets_engine(self):
        client = hvac.Client(url=self.server_id, token=self.token)
        try:
            client.sys.read_mount_configuration(path=self.org_name)
            print(f'Secrets engine at path "{self.org_name}" is already enabled.')
        except (InvalidPath, InvalidRequest):
            print(f'Secrets engine at path "{self.org_name}" is not enabled. Enabling it now...')
            client.sys.enable_secrets_engine(
                backend_type='kv',
                path=self.org_name,
                options={'version': '2'}
            )
            print(f'Secrets engine at path "{self.org_name}" has been enabled.')

    def enable(self):
        client = hvac.Client(url=self.server_id, token=self.token)
        client.sys.enable_secrets_engine(
            backend_type='kv',
            path='kv',
            options={'version': '2'} 
        )
        print("Enabled KV version 2 engine at 'kv' path.")

        self.check_and_enable_secrets_engine()

        client.sys.enable_secrets_engine(
            backend_type='kv', 
            path='organization', 
            options={'version': '2'}
        )
        print(f'Secrets engine at path "organization" has been enabled.')
        data = {
            "tenant": self.tenant_id,
        }
        client.secrets.kv.v2.create_or_update_secret(
            path=f"{self.org_name}",
            secret=data,
            mount_point='organization' 
        )
        client.sys.enable_auth_method(
            method_type='userpass', 
            path=f'userpass-{self.org_name}'
        )
        print(f'Authentication method has been successfully enabled at path: userpass-{self.org_name}.')