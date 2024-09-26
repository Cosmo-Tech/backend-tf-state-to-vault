import logging
import sys
import os
import hvac
from hvac.exceptions import InvalidPath, InvalidRequest

logger = logging.getLogger("Babylon")


class EnableNewTenant:

    def __init__(self, version_engine: str = "v1"):
        for v in [
            "VAULT_ADDR",
            "VAULT_TOKEN",
            "TENANT_ID",
            "ORGANIZATION_NAME"
        ]:
            if v not in os.environ:
                logger.error(f" {v} is missing")
                sys.exit(1)

        self.version_engine = version_engine
        self.server_id = os.environ.get("VAULT_ADDR")
        self.token = os.environ.get("VAULT_TOKEN")
        self.org_name = os.environ.get("ORGANIZATION_NAME")
        self.tenant_id = os.environ.get("TENANT_ID")

    def check_and_enable_secrets_engine(self, secret_engine: str = "kv"):
        client = hvac.Client(url=self.server_id, token=self.token)
        try:
            client.sys.read_mount_configuration(path=secret_engine)
            print(f'Secrets engine at path "{secret_engine}" is already enabled.')
        except (InvalidPath, InvalidRequest):
            print(
                f'Secrets engine at path "{secret_engine}" is not enabled. Enabling it now...'
            )
            client.sys.enable_secrets_engine(

                backend_type="kv", path=secret_engine, options={"version": self.version_engine[-1]}
            )
            print(f'Secrets engine at path "{secret_engine}" has been enabled.')

    def enable(self, secret_engine: str = "kv"):
        client = hvac.Client(url=self.server_id, token=self.token)
        try:
            client.sys.enable_secrets_engine(
                backend_type="kv", path=secret_engine, options={"version": self.version_engine[-1]}
            )
        except Exception as ex:
            print("Warning", ex)
        print("Enabled KV version 2 engine at 'kv' path.")
        self.check_and_enable_secrets_engine(secret_engine=secret_engine)
        try:
            client.sys.enable_secrets_engine(
                backend_type="kv", path="organization", options={"version": self.version_engine[-1]}
            )
        except Exception as ex:
            print("Warning", ex)
        print('Secrets engine at path "organization" has been enabled.')
        data = {
            "tenant": self.tenant_id,
        }
        try:
            if self.version_engine == "v1":
                client.write(path=f"organization/{self.org_name}", **data)
            else:
                client.secrets.kv.v2.create_or_update_secret(
                    path=f"{self.org_name}", secret=data, mount_point="organization"
                )
        except Exception as ex:
            print("Warning", ex)
        try:
            client.sys.enable_auth_method(
                method_type="userpass", path=f"userpass-{self.org_name}"
            )
        except Exception as ex:
            print("Warning", ex)
        print(
            f"Authentication method has been successfully enabled at path: userpass-{self.org_name}."
        )
