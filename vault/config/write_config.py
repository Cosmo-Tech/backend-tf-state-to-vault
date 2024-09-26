import os
import sys
import json
import logging
import hvac
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class WriteConfig:

    def __init__(
        self,
        version_engine: str = "v2",
        local_file=None,
        use_azure=False,
        from_tfstate: bool = False,
    ):
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
        self.from_tfstate = from_tfstate
        self.server_id = os.environ.get("VAULT_ADDR")
        self.token = os.environ.get("VAULT_TOKEN")
        self.org_name = os.environ.get("ORGANIZATION_NAME")
        self.tenant_id = os.environ.get("TENANT_ID")
        self.cluster_name = os.environ.get("CLUSTER_NAME")
        self.storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        self.storage_secret = os.environ.get("STORAGE_ACCOUNT_KEY")
        self.storage_container = os.environ.get("STORAGE_CONTAINER")
        self.tfstate_blob_name = os.environ.get("TFSTATE_BLOB_NAME")

        self.local_file = local_file
        self.use_azure = use_azure and not local_file
        self.vault_client = hvac.Client(url=self.server_id, token=self.token)
        self.blob_client = None
        self.secrets = None

        if self.use_azure:
            self._init_blob_client()
        if self.local_file:
            self._read_or_create_local_state()
        else:
            self._read_or_create_azure_state()

        self.prefix = f"{self.tenant_id}/babylon/config"
        self.prefix_client = f"{self.tenant_id}/babylon"
        self.prefix_platform = f"{self.tenant_id}/platform"

    def _init_blob_client(self):
        try:
            account_key = (
                f"AccountKey={self.storage_secret};EndpointSuffix=core.windows.net"
            )
            conn_str = f"DefaultEndpointsProtocol=https;AccountName={self.storage_name};{account_key}"
            self.blob_client = BlobServiceClient.from_connection_string(conn_str)
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob client: {str(e)}")

    def _read_or_create_local_state(self):
        if os.path.exists(self.local_file):
            try:
                with open(self.local_file, "r") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                logger.warning(
                    f"Invalid JSON in {self.local_file}. Creating new state."
                )
                self.data = {"outputs": {}}
        else:
            logger.info(f"File {self.local_file} not found. Creating new state.")
            self.data = {"outputs": {}}

    def _read_or_create_azure_state(self):
        try:
            if self.blob_client:
                container_client = self.blob_client.get_container_client(
                    self.storage_container
                )
                blob_client = container_client.get_blob_client(self.tfstate_blob_name)
                try:
                    self.state = blob_client.download_blob().readall()
                    self.data = json.loads(self.state)
                except Exception as e:
                    logger.info(
                        f"Blob not found or invalid. Creating new state. Error: {str(e)}"
                    )
                    self.data = {"outputs": {}}
        except Exception as e:
            logger.error(f"Failed to access Azure Blob: {str(e)}")
            # self.data = {"outputs": {}}

    def upload_config(self, schema: str, data: dict):
        schema_ = schema
        if self.version_engine == "v1":
            schema_ = f"{self.org_name}/{schema}"
        self._write_to_vault(schema=schema_, data=data)

    def _write_to_local(self, key: str, data: dict):
        try:
            self.data.setdefault("outputs", {})[key] = {"value": data}
            with open(self.local_file, "w") as f:
                json.dump(self.data, f, indent=2)
            logger.info(f"Successfully wrote {key} to local file")
        except Exception as e:
            logger.error(f"Failed to write to local file: {str(e)}")

    def _write_to_azure(self, key: str, data: dict):
        try:
            self.data.setdefault("outputs", {})[key] = {"value": data}
            container_client = self.blob_client.get_container_client(
                self.storage_container
            )
            blob_client = container_client.get_blob_client(self.tfstate_blob_name)
            blob_client.upload_blob(json.dumps(self.data), overwrite=True)
            logger.info(f"Successfully wrote {key} to Azure Blob")
        except Exception as e:
            logger.error(f"Failed to write to Azure Blob: {str(e)}")

    def _write_to_vault(self, schema: str, data: dict):
        try:
            if self.version_engine == "v1":
                self.vault_client.write(path=schema, **data)
            else:
                self.vault_client.secrets.kv.v2.create_or_update_secret(
                    path=schema, secret=data, mount_point=self.org_name
                )
            print(f"Successfully wrote {schema} to Vault")
        except Exception as e:
            logger.error(f"Failed to write to Vault: {str(e)}")

    def set_babylon_client_secret(self, platform_id: str):
        data = self.data
        babylon_secret = (
            ""
            if "out_babylon_sp_client_secret" not in data["outputs"]
            else data["outputs"]["out_babylon_sp_client_secret"]["value"]
        )
        client_secret = dict(secret=babylon_secret)
        self.upload_config(f"{self.prefix_client}/{platform_id}/client", client_secret)
        return self

    def set_storage_client_secret(self, platform_id: str):
        data = self.data
        storage_acc_secret = (
            ""
            if "out_azure_storage_account_key" not in data["outputs"]
            else data["outputs"]["out_azure_storage_account_key"]["value"]
        )
        client_secret = dict(secret=storage_acc_secret)
        self.upload_config(
            f"{self.prefix_platform}/{platform_id}/storage/account", client_secret
        )
        return self

    def write_acr(self, platform_id):
        data = self.data
        acr_login_server = (
            ""
            if "out_acr_login_server" not in data["outputs"]
            else data["outputs"]["out_acr_login_server"]["value"]
        )
        acr = {
            "login_server": acr_login_server,
            "simulator_repository": "",
            "simulator_version": "",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/acr", acr)
        return self

    def write_adt(self, platform_id):
        adt = {
            "built_owner_id": "bcd981a7-7f74-457b-83e1-cceb9e632ffe",
            "built_reader_id": "d57506d4-4c8d-48b1-8587-93c323f6a5a3",
            "digital_twin_url": "",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/adt", adt)
        return self

    def write_app(self, platform_id):
        app = {"app_id": "", "name": "", "object_id": "", "principal_id": ""}
        self.upload_config(f"{self.prefix}/{platform_id}/app", app)
        return self

    def write_adx(self, platform_id):
        data = self.data
        cluster_name = (
            ""
            if "out_adx_cluster_name" not in data["outputs"]
            else data["outputs"]["out_adx_cluster_name"]["value"]
        )
        adx_uri = (
            ""
            if "out_adx_cluster_uri" not in data["outputs"]
            else data["outputs"]["out_adx_cluster_uri"]["value"]
        )
        cluster_principal_id = (
            ""
            if "out_adx_cluster_principal_id" not in data["outputs"]
            else data["outputs"]["out_adx_cluster_principal_id"]["value"]
        )
        adx = {
            "built_contributor_id": "b24988ac-6180-42a0-ab88-20f7382dd24c",
            "built_owner_id": "8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
            "cluster_name": cluster_name,
            "cluster_principal_id": cluster_principal_id,
            "cluster_uri": adx_uri,
            "database_name": "",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/adx", adx)
        return self

    def write_api(self, platform_id):
        data = self.data
        scope = (
            ""
            if "out_api_cosmo_scope" not in data["outputs"]
            else f"{data['outputs']['out_api_cosmo_scope']['value']}"
        )
        url = (
            ""
            if "out_api_cosmo_url" not in data["outputs"]
            else f"{data['outputs']['out_api_cosmo_url']['value']}"
        )
        api = {
            "connector.adt_id": "",
            "connector.adt_version": "",
            "connector.storage_id": "",
            "connector.storage_version": "",
            "connector.twin_id": "",
            "connector.twin_version": "",
            "dataset.adt_id": "",
            "dataset.storage_id": "",
            "dataset.twin_id": "",
            "organization_id": "",
            "organization_url": "",
            "run_templates": "",
            "scope": scope,
            "send_scenario_metadata_to_event_hub": True,
            "solution_id": "",
            "url": url,
            "use_dedicated_event_hub_namespace": True,
            "workspace_id": "",
            "workspace_key": "",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/api", api)
        return self

    def write_azure(self, platform_id):
        data = self.data
        resource_group_name = (
            ""
            if "out_azure_tenant_resource_group" not in data["outputs"]
            else data["outputs"]["out_azure_tenant_resource_group"]["value"]
        )
        resource_location = (
            ""
            if "out_azure_resource_location" not in data["outputs"]
            else data["outputs"]["out_azure_resource_location"]["value"]
        )
        storage_account_name = (
            ""
            if "out_azure_storage_account_name" not in data["outputs"]
            else data["outputs"]["out_azure_storage_account_name"]["value"]
        )
        subscription_id = (
            ""
            if "out_azure_subscription_id" not in data["outputs"]
            else data["outputs"]["out_azure_subscription_id"]["value"]
        )
        azure = {
            "cli_client_id": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
            "email": "",
            "eventhub_built_contributor_id": "b24988ac-6180-42a0-ab88-20f7382dd24c",
            "eventhub_built_data_receiver": "a638d3c7-ab3a-418d-83e6-5f17a39d4fde",
            "eventhub_built_data_sender": "2b629674-e913-4c01-ae53-ef4638d8f975",
            "function_artifact_url": "",
            "resource_group_name": resource_group_name,
            "resource_location": resource_location,
            "storage_account_name": storage_account_name,
            "storage_blob_reader": "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1",
            "subscription_id": subscription_id,
            "team_id": "",
            "user_principal_id": "",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/azure", azure)
        return self

    def write_babylon(self, platform_id):
        data = self.data
        babylon_client_id = (
            ""
            if "out_tenant_sp_client_id" not in data["outputs"]
            else data["outputs"]["out_tenant_sp_client_id"]["value"]
        )
        babylon_principal_id = (
            ""
            if "out_tenant_sp_object_id" not in data["outputs"]
            else data["outputs"]["out_tenant_sp_object_id"]["value"]
        )
        babylon = {"client_id": babylon_client_id, "principal_id": babylon_principal_id}
        self.upload_config(f"{self.prefix}/{platform_id}/babylon", babylon)
        return self

    def write_github(self, platform_id):
        github = {
            "branch": "",
            "organization": "",
            "repository": "",
            "run_url": "",
            "workflow_path": "",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/github", github)
        return self

    def write_plaftorm(self, platform_id):
        data = self.data
        platform_sp_client_id = (
            ""
            if "out_tenant_sp_client_id" not in data["outputs"]
            else data["outputs"]["out_tenant_sp_client_id"]["value"]
        )
        platform_sp_object_id = (
            ""
            if "out_tenant_sp_object_id" not in data["outputs"]
            else data["outputs"]["out_tenant_sp_object_id"]["value"]
        )
        platform = {
            "app_id": platform_sp_client_id,
            "principal_id": platform_sp_object_id,
            "scope_id": "6332363e-bcba-4c4a-a605-c25f23117400",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/platform", platform)
        return self

    def write_powerbi(self, platform_id):
        powerbi = {
            "scope": "https://analysis.windows.net/powerbi/api/.default",
            "dashboard_view": "",
            "group_id": "",
            "scena_write_to_azurerio_view": "",
            "workspace.id": "",
            "workspace.name": "",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/powerbi", powerbi)
        return self

    def write_webapp(self, platform_id):
        webapp = {
            "deployment_name": "",
            "enable_insights": False,
            "hostname": "",
            "insights_instrumentation_key": "",
            "location": "",
            "static_domain": "",
        }
        self.upload_config(f"{self.prefix}/{platform_id}/webapp", webapp)
        return self

    def write_all_config(self, platform_id: str):
        self.write_acr(platform_id=platform_id)
        self.write_adt(platform_id=platform_id)
        self.write_app(platform_id=platform_id)
        self.write_adx(platform_id=platform_id)
        self.write_api(platform_id=platform_id)
        self.write_azure(platform_id=platform_id)
        self.write_babylon(platform_id=platform_id)
        self.write_github(platform_id=platform_id)
        self.write_plaftorm(platform_id=platform_id)
        self.write_powerbi(platform_id=platform_id)
        self.write_webapp(platform_id=platform_id)
        self.set_storage_client_secret(platform_id=platform_id)
        self.set_babylon_client_secret(platform_id=platform_id)
        return self

    def write_config(self, resource: str, platform_id: str):
        if resource == "acr":
            self.write_acr(platform_id=platform_id)
        if resource == "adt":
            self.write_adt(platform_id=platform_id)
        if resource == "adx":
            self.write_adx(platform_id=platform_id)
        if resource == "app":
            self.write_app(platform_id=platform_id)
        if resource == "api":
            self.write_api(platform_id=platform_id)
        if resource == "azure":
            self.write_azure(platform_id=platform_id)
        if resource == "babylon":
            self.write_babylon(platform_id=platform_id)
        if resource == "github":
            self.write_github(platform_id=platform_id)
        if resource == "platform":
            self.write_plaftorm(platform_id=platform_id)
        if resource == "powerbi":
            self.write_powerbi(platform_id=platform_id)
        if resource == "webapp":
            self.write_webapp(platform_id=platform_id)
