import os
import sys
import logging
import hvac

logger = logging.getLogger("Babylon")


class DeleteConfig:

    def __init__(self, version_engine: str = "v2"):
        for v in [
            "VAULT_ADDR",
            "VAULT_TOKEN",
            "TENANT_ID",
            "ORGANIZATION_NAME",
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
        self.storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        self.storage_secret = os.environ.get("STORAGE_ACCOUNT_KEY")
        self.storage_container = os.environ.get("STORAGE_CONTAINER")
        self.tfstate_blob_name = os.environ.get("TFSTATE_BLOB_NAME")

        self.org_tenant = f"{self.tenant_id}"
        self.prefix = f"{self.org_tenant}/babylon/config"

    def delete_get_config(self, resource: str, platform_id: str):
        if resource == "acr":
            self.delete_acr(platform_id)
        if resource == "adt":
            self.delete_adt(platform_id)
        if resource == "adx":
            self.delete_adx(platform_id)
        if resource == "app":
            self.delete_app(platform_id)
        if resource == "api":
            self.delete_api(platform_id)
        if resource == "azure":
            self.delete_azure(platform_id)
        if resource == "babylon":
            self.delete_babylon(platform_id)
        if resource == "github":
            self.delete_github(platform_id)
        if resource == "platform":
            self.delete_plaftorm(platform_id)
        if resource == "powerbi":
            self.delete_powerbi(platform_id)
        if resource == "webapp":
            self.delete_webapp(platform_id)
        if resource == "client":
            self.delete_babylon_client_secret(platform_id)
        if resource == "storage":
            self.delete_storage_client_secret(platform_id)

    def delete_config(self, schema: str):
        client = hvac.Client(url=self.server_id, token=self.token)
        if self.version_engine == "v1":
            print(f"deleting {self.org_name}/{schema}")
            client.delete(path=f"{self.org_name}/{schema}")
        else:
            client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=schema,
                mount_point=self.org_name,
            )
        return self

    def delete_babylon_client_secret(self, platform_id: str):
        self.delete_config(f"{self.org_tenant}/babylon/{platform_id}/client")
        return self

    def delete_storage_client_secret(self, platform_id: str):
        self.platform_prefix = f"{self.org_tenant}/platform/{platform_id}"
        self.delete_config(
            f"{self.platform_prefix}/storage/account",
        )
        return self

    def delete_acr(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/acr")
        return self

    def delete_adt(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/adt")
        return self

    def delete_app(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/app")
        return self

    def delete_adx(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/adx")
        return self

    def delete_api(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/api")
        return self

    def delete_azure(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/azure")
        return self

    def delete_babylon(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/babylon")
        return self

    def delete_github(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/github")
        return self

    def delete_plaftorm(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/platform")
        return self

    def delete_powerbi(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/powerbi")
        return self

    def delete_webapp(self, platform_id):
        self.delete_config(f"{self.prefix}/{platform_id}/webapp")
        return self

    def delete_all_config(self, platform_id):
        self.delete_acr(platform_id)
        self.delete_adt(platform_id)
        self.delete_app(platform_id)
        self.delete_adx(platform_id)
        self.delete_api(platform_id)
        self.delete_azure(platform_id)
        self.delete_babylon(platform_id)
        self.delete_github(platform_id)
        self.delete_plaftorm(platform_id)
        self.delete_powerbi(platform_id)
        self.delete_webapp(platform_id)
        self.delete_babylon_client_secret(platform_id)
        self.delete_storage_client_secret(platform_id)
        return self
