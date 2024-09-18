import logging
import sys
import os
import hvac

logger = logging.getLogger("Babylon")


class DeletePolicies:

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

    def delete_policy(self, policy_name):
        client = hvac.Client(url=self.server_id, token=self.token)

        try:
            # Delete the policy
            client.sys.delete_policy(name=policy_name)
            print(f"Policy '{policy_name}' has been deleted.")
        except hvac.exceptions.InvalidRequest as e:
            print(f"Invalid request: {e}")
        except hvac.exceptions.InvalidRequest as e:
            print(f"Policy '{policy_name}' does not exist or could not be deleted: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
