import pathlib
import json
import logging
import sys
import os
import hvac
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class AddSecrets:

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

        self.secrets = None

        _secrets = pathlib.Path("secrets.json")
        if _secrets.exists():
            with open(_secrets) as f:
                self.secrets = json.loads(f.read())
        else:
            self.dowload_ftstate()
            self.secrets = json.loads(self.state)

        if self.secrets is None:
            logger.error("secrets is missing")
            sys.exit(1)

        tenant = f"{self.tenant_id}"
        self.prefix_secrets = f"{tenant}/{self.platform_name}"

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

    def upload_secrets(self, schema: str, data: dict):
        client = hvac.Client(url=self.server_id, token=self.token)
        client.secrets.kv.v2.create_or_update_secret(path=schema, secret=data, mount_point=self.org_name)
        return self

    def get_output_value(self, key):
        return self.secrets["outputs"][key]["value"] if key in self.secrets["outputs"] else ""

    def check_file_secret(self, file_path):
        _secrets = pathlib.Path(file_path)
        if _secrets.exists():
            with open(_secrets) as f:
                self.secrets = json.loads(f.read())
        else:
            self.dowload_ftstate()
            self.secrets = json.loads(self.state)

        if self.secrets is None:
            logger.error("secrets is missing")
            sys.exit(1)

    def add_patform_secrets(self, file_path):
        self.check_file_secret(file_path)
        api_version = self.get_output_value("out_API_VERSION")
        acr_server = self.get_output_value("out_ACR_SERVER")
        acr_username = self.get_output_value("out_ACR_USERNAME")
        acr_password = self.get_output_value("out_ACR_PASSWORD")
        acr_registry_url = self.get_output_value("out_ACR_REGISTRY_URL")
        host_cosmotech_api = self.get_output_value("out_HOST_COSMOTECH_API")
        identity_authorization_url = self.get_output_value("out_IDENTITY_AUTHORIZATION_URL")
        identity_token_url = self.get_output_value("out_IDENTITY_TOKEN_URL")
        monitoring_namespace = self.get_output_value("out_MONITORING_NAMESPACE")
        namespace = self.get_output_value("out_NAMESPACE")
        argo_service_account_name = self.get_output_value("out_ARGO_SERVICE_ACCOUNT_NAME")
        azure_tenant_id = self.get_output_value("out_AZURE_TENANT_ID")
        azure_appid_uri = self.get_output_value("out_AZURE_APPID_URI")
        azure_storage_account_key = self.get_output_value("out_AZURE_STORAGE_ACCOUNT_KEY")
        azure_storage_account_name = self.get_output_value("out_AZURE_STORAGE_ACCOUNT_NAME")
        azure_credentials_client_id = self.get_output_value("out_AZURE_CREDENTIALS_CLIENT_ID")
        azure_credentials_client_secret = self.get_output_value("out_AZURE_CREDENTIALS_CLIENT_SECRET")
        azure_credentials_customer_client_id = self.get_output_value("out_AZURE_CREDENTIALS_CUSTOMER_CLIENT_ID")
        azure_credentials_customer_client_secret = self.get_output_value("out_AZURE_CREDENTIALS_CUSTOMER_CLIENT_SECRET")
        adx_base_uri = self.get_output_value("out_ADX_BASE_URI")
        adx_ingest_uri = self.get_output_value("out_ADX_INGEST_URI")
        eventbus_base_uri = self.get_output_value("out_EVENTBUS_BASE_URI")
        host_postgres = self.get_output_value("out_HOST_POSTGRES")
        host_redis = self.get_output_value("out_HOST_REDIS")
        host_redis_password = self.get_output_value("out_HOST_REDIS_PASSWORD")
        host_argo_workflows_server = self.get_output_value("out_HOST_ARGO_WORKFLOWS_SERVER")
        rds_hub_listener = self.get_output_value("out_RDS_HUB_LISTENER")
        rds_hub_sender = self.get_output_value("out_RDS_HUB_SENDER")
        rds_storage_admin = self.get_output_value("out_RDS_STORAGE_ADMIN")
        rds_storage_reader = self.get_output_value("out_RDS_STORAGE_READER")
        rds_storage_writer = self.get_output_value("out_RDS_STORAGE_WRITER")
        host_rds = self.get_output_value("out_HOST_RDS")
        host_rds_postgres = self.get_output_value("out_HOST_RDS_POSTGRES")
        spring_application_json = self.get_output_value("out_SPRING_APPLICATION_JSON")
        secrets = {
            "API_VERSION": api_version,
            "ACR_SERVER": acr_server,
            "ACR_USERNAME": acr_username,
            "ACR_PASSWORD": acr_password,
            "ACR_REGISTRY_URL": acr_registry_url,
            "HOST_COSMOTECH_API": host_cosmotech_api,
            "IDENTITY_AUTHORIZATION_URL": identity_authorization_url,
            "IDENTITY_TOKEN_URL": identity_token_url,
            "MONITORING_NAMESPACE": monitoring_namespace,
            "NAMESPACE": namespace,
            "ARGO_SERVICE_ACCOUNT_NAME": argo_service_account_name,
            "AZURE_TENANT_ID": azure_tenant_id,
            "AZURE_APPID_URI": azure_appid_uri,
            "AZURE_STORAGE_ACCOUNT_KEY": azure_storage_account_key,
            "AZURE_STORAGE_ACCOUNT_NAME": azure_storage_account_name,
            "AZURE_CREDENTIALS_CLIENT_ID": azure_credentials_client_id,
            "AZURE_CREDENTIALS_CLIENT_SECRET": azure_credentials_client_secret,
            "AZURE_CREDENTIALS_CUSTOMER_CLIENT_ID": azure_credentials_customer_client_id,
            "AZURE_CREDENTIALS_CUSTOMER_CLIENT_SECRET": azure_credentials_customer_client_secret,
            "ADX_BASE_URI": adx_base_uri,
            "ADX_INGEST_URI": adx_ingest_uri,
            "EVENTBUS_BASE_URI": eventbus_base_uri,
            "HOST_POSTGRES": host_postgres,
            "HOST_REDIS": host_redis,
            "HOST_REDIS_PASSWORD": host_redis_password,
            "HOST_ARGO_WORKFLOWS_SERVER": host_argo_workflows_server,
            "RDS_HUB_LISTENER": rds_hub_listener,
            "RDS_HUB_SENDER": rds_hub_sender,
            "RDS_STORAGE_ADMIN": rds_storage_admin,
            "RDS_STORAGE_READER": rds_storage_reader,
            "RDS_STORAGE_WRITER": rds_storage_writer,
            "HOST_RDS": host_rds,
            "HOST_RDS_POSTGRES": host_rds_postgres,
            "SPRING_APPLICATION_JSON": spring_application_json
        }
        self.upload_secrets(f"{self.prefix_secrets}/{self.platform_name}-platform-secrets", secrets)
        return self
