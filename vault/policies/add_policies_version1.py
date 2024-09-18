import logging
import sys
import os
from hvac import Client

logger = logging.getLogger("Babylon")


class AddPlocies:

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

    def create_policies(self):
        client = Client(url=self.server_id, token=self.token)
        admin_policy = f"""
        path "{self.org_name}/{self.tenant_id}/*" {{
            capabilities = ["create", "read", "update", "delete", "list"]
        }}
        path "organization/*" {{
            capabilities = ["create", "read", "update", "delete", "list"]
        }}
        path "{self.org_name}/*" {{
            capabilities = ["create", "read", "update", "delete", "list"]
        }}
        path "auth/userpass-{self.org_name}/users/*" {{
            capabilities = ["update"]
            allowed_parameters = {{
                "password" = []
            }}
        }}
        path "auth/token/create" {{
            capabilities = ["create", "update"]
        }}
        path "auth/token/renew" {{
            capabilities = ["update"]
        }}
        path "auth/token/revoke" {{
            capabilities = ["update"]
        }}
        """
        contributor_policy = f"""
        path "{self.org_name}/{self.tenant_id}/*" {{
            capabilities = ["create", "read", "update", "list"]
        }}
        path "{self.org_name}/*" {{
            capabilities = ["create", "read", "update", "list"]
        }}
        path "organization/*" {{
            capabilities = ["create", "read", "update", "list"]
        }}
        path "auth/userpass-{self.org_name}/users/*" {{
            capabilities = ["update"]
            allowed_parameters = {{
                "password" = []
            }}
        }}
        path "auth/token/create" {{
            capabilities = ["create", "update"]
        }}
        path "auth/token/renew" {{
            capabilities = ["update"]
        }}
        """
        auth_methods = client.sys.list_auth_methods()
        accessor = auth_methods[f'userpass-{self.org_name}/']['accessor']

        user_policy = f"""
        path "{self.org_name}/{self.tenant_id}/users/{{{{identity.entity.metadata.email}}}}/*" {{
            capabilities = ["create", "update", "patch", "read", "delete", "list"]
        }}
        path "{self.org_name}/{self.tenant_id}/projects/{{{{identity.entity.metadata.project}}}}/*" {{
            capabilities = ["create", "update", "patch", "read", "delete", "list"]
        }}
        path "{self.org_name}/*" {{
            capabilities = ["read", "list"]
        }}
        path "organization/*" {{
            capabilities = ["read", "list"]
        }}
        path "auth/userpass-{self.org_name}/users/{{{{identity.entity.aliases.{accessor}.name}}}}" {{
            capabilities = ["update"]
            allowed_parameters = {{
                "password" = []
            }}
        }}
        path "auth/token/create" {{
            capabilities = ["create", "update"]
        }}
        path "auth/token/renew" {{
            capabilities = ["update"]
        }}
        path "{self.org_name}/{self.tenant_id}/platform/*" {{
            capabilities = ["read", "list"]
        }}
        path "{self.org_name}/{self.tenant_id}/global/*" {{
            capabilities = ["read", "list"]
        }}
        path "{self.org_name}/{self.tenant_id}/global/*" {{
            capabilities = ["read", "list"]
        }}
        path "{self.org_name}/{self.tenant_id}/cluster/*" {{
            capabilities = ["read", "list"]
        }}
        path "{self.org_name}/{self.tenant_id}/*" {{
            capabilities = ["read", "list"]
        }}
        path "{self.org_name}/*" {{
            capabilities = ["read", "list"]
        }}
        """

        external_policy = f"""
        path "auth/token/create" {{
            capabilities = ["create", "update"]
        }}
        path "auth/token/renew" {{
            capabilities = ["update"]
        }}
        path "{self.org_name}/platforms/*" {{
            capabilities = ["read", "list"]
        }}
        path "organization/*" {{
            capabilities = ["read", "list"]
        }}
        path "organization/{self.org_name}" {{
            capabilities = ["read", "list"]
        }}
        """

        client.sys.create_or_update_policy(name=f'{self.org_name}_admin', policy=admin_policy)
        client.sys.create_or_update_policy(name=f'{self.org_name}_contributor', policy=contributor_policy)
        client.sys.create_or_update_policy(name=f'{self.org_name}_user', policy=user_policy)
        client.sys.create_or_update_policy(name=f'{self.org_name}_external', policy=external_policy)
