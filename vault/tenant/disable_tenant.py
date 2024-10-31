import logging
import sys
import os
import hvac

logger = logging.getLogger("Babylon")


class DisableTenant:

    def __init__(self):
        for v in [
            "VAULT_ADDR",
            "VAULT_TOKEN",
            "ORGANIZATION_NAME",
            "TENANT_ID",
        ]:
            if v not in os.environ:
                logger.error(f" {v} is missing")
                sys.exit(1)

        self.server_id = os.environ.get("VAULT_ADDR")
        self.token = os.environ.get("VAULT_TOKEN")
        self.org_name = os.environ.get("ORGANIZATION_NAME")
        self.tenant_id = os.environ.get("TENANT_ID")

    def disable(self, secret_engine: str = "kv"):
        client = hvac.Client(url=self.server_id, token=self.token)
        # Disable the secrets engine
        client.sys.disable_secrets_engine(path=secret_engine)
        print('Secrets engine at path "kv" has been disabled.')
        print(f'Secrets engine at path "{self.org_name}" has been disabled.')
        client.sys.disable_secrets_engine(path=self.org_name)
        print(f'Secrets engine at path "{self.org_name}" has been disabled.')
        client.sys.disable_secrets_engine(path="organization")
        print('Secrets engine at path "organization" has been disabled.')
        client.sys.disable_auth_method(path=f"userpass-{self.org_name}")
        print(
            f'Authentication method at path "userpass-{self.org_name}" has been disabled.'
        )
