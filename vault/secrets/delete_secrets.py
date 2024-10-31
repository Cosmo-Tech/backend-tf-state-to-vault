import logging
import sys
import os
import hvac

logger = logging.getLogger("Babylon")


class DeletesSecrets:

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
        self.prefix_secrets = f"{tenant}/{self.platform_name}"

    def delete_secrets(self):
        client = hvac.Client(url=self.server_id, token=self.token)
        client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=f"{self.prefix_secrets}/{self.platform_name}-platform-secrets",
            mount_point=self.org_name,
        )
        return self
