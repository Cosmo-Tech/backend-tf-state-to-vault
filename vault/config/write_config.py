import os
import re
import sys
import json
import pathlib
import logging
import hvac
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("Babylon")


class WriteConfig:
    def dowload_ftstate(self):
        prefix = "DefaultEndpointsProtocol=https;"
        prefix += f"AccountName={self.storage_name}"
        conn_str = f"{prefix};AccountKey={self.storage_secret};"
        conn_str += "EndpointSuffix=core.windows.net"
        self.blob_client = BlobServiceClient.from_connection_string(conn_str)
        try:
            service = self.blob_client.get_container_client(
                container=self.storage_container
            )
            blob = service.get_blob_client(blob=self.tfstate_blob_name)
            state = blob.download_blob(encoding="utf-8").content_as_bytes()
            self.state = state
        except Exception:
            self.state = "{}" 
            logger.info("blob not found")

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

        self.data = None
        self.secrets = None
        _file = pathlib.Path("state.json")
        if _file.exists():
            with open(_file) as f:
                self.data = json.loads(f.read())
        else:
            self.dowload_ftstate()
            self.data = json.loads(self.state)

        if self.data is None:
            logger.error("data is missing")
            sys.exit(1)
        
        tenant = f"{self.tenant_id}"
        self.prefix = f"{tenant}/babylon/config/{self.platform_name}"
        self.prefix_client = f"{tenant}/babylon/{self.platform_name}"
        self.prefix_platform = f"{tenant}/platform"

    def upload_config(self, schema: str, data: dict):
        client = hvac.Client(url=self.server_id, token=self.token)
        client.secrets.kv.v2.create_or_update_secret(
            path=schema,
            secret=data,
            mount_point=self.org_name
        )
        return self
    
    def set_babylon_client_secret(self):
        acr_login_server = (
            ""
            if "out_babylon_client_secret" not in self.data["outputs"]
            else self.data["outputs"]["out_babylon_client_secret"]["value"]
        )
        client_secret = dict(secret=acr_login_server)
        self.upload_config(f"{self.prefix_client}/client", client_secret)
        return self

    def set_storage_client_secret(self):
        storage_acc_secret = (
            ""
            if "out_storage_account_secret" not in self.data["outputs"]
            else self.data["outputs"]["out_storage_account_secret"]["value"]
        )
        client_secret = dict(secret=storage_acc_secret)
        self.upload_config(
            f"{self.prefix_platform}/{self.platform_name}/storage/account",
            client_secret,
        )
        return self

    def write_acr(self):
        acr_login_server = (
            ""
            if "out_acr_login_server" not in self.data["outputs"]
            else self.data["outputs"]["out_acr_login_server"]["value"]
        )
        acr = {
            "login_server": acr_login_server,
            "simulator_repository": "",
            "simulator_version": "",
        }
        self.upload_config(f"{self.prefix}/acr", acr)
        return self

    def write_adt(self):
        adt = {
            "built_owner_id": "bcd981a7-7f74-457b-83e1-cceb9e632ffe",
            "built_reader_id": "d57506d4-4c8d-48b1-8587-93c323f6a5a3",
            "digital_twin_url": "",
        }
        self.upload_config(f"{self.prefix}/adt", adt)
        return self

    def write_app(self):
        app = {"app_id": "", "name": "", "object_id": "", "principal_id": ""}
        self.upload_config(f"{self.prefix}/app", app)
        return self

    def write_adx(self):
        adx_uri = (
            ""
            if "out_adx_uri" not in self.data["outputs"]
            else self.data["outputs"]["out_adx_uri"]["value"]
        )
        ckrgx = re.compile("^https:\\/\\/([a-zA-Z|-].+)\\..+\\.kusto\\..+$")
        match_content = ckrgx.match(adx_uri)
        if not match_content:
            print("error with uri adx cluster")
            return self
        cluster_name = match_content.groups()
        cluster_name = cluster_name[0] if len(cluster_name) else ""
        cluster_principal_id = (
            ""
            if "out_cluster_adx_principal_id" not in self.data["outputs"]
            else self.data["outputs"]["out_cluster_adx_principal_id"]["value"]
        )
        adx = {
            "built_contributor_id": "b24988ac-6180-42a0-ab88-20f7382dd24c",
            "built_owner_id": "8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
            "cluster_name": cluster_name,
            "cluster_principal_id": cluster_principal_id,
            "cluster_uri": adx_uri,
            "database_name": "",
        }
        self.upload_config(f"{self.prefix}/adx", adx)
        return self

    def write_api(self):
        scope = (
            ""
            if "out_cosmos_api_scope" not in self.data["outputs"]
            else f"{self.data['outputs']['out_cosmos_api_scope']['value']}"
        )
        url = (
            ""
            if "out_cosmos_api_url" not in self.data["outputs"]
            else f"{self.data['outputs']['out_cosmos_api_url']['value']}"
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
        self.upload_config(f"{self.prefix}/api", api)
        return self

    def write_azure(self):
        resource_group_name = (
            ""
            if "out_tenant_resource_group_name" not in self.data["outputs"]
            else self.data["outputs"]["out_tenant_resource_group_name"]["value"]
        )
        resource_location = (
            ""
            if "out_resource_location" not in self.data["outputs"]
            else self.data["outputs"]["out_resource_location"]["value"]
        )
        storage_account_name = (
            ""
            if "out_storage_account_name" not in self.data["outputs"]
            else self.data["outputs"]["out_storage_account_name"]["value"]
        )
        subscription_id = (
            ""
            if "out_subscription_id" not in self.data["outputs"]
            else self.data["outputs"]["out_subscription_id"]["value"]
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
        self.upload_config(f"{self.prefix}/azure", azure)
        return self

    def write_babylon(self):
        babylon_client_id = (
            ""
            if "out_babylon_client_id" not in self.data["outputs"]
            else self.data["outputs"]["out_babylon_client_id"]["value"]
        )
        babylon_principal_id = (
            ""
            if "out_babylon_principal_id" not in self.data["outputs"]
            else self.data["outputs"]["out_babylon_principal_id"]["value"]
        )
        babylon = {"client_id": babylon_client_id, "principal_id": babylon_principal_id}
        self.upload_config(f"{self.prefix}/babylon", babylon)
        return self

    def write_github(self):
        github = {
            "branch": "",
            "organization": "",
            "repository": "",
            "run_url": "",
            "workflow_path": "",
        }
        self.upload_config(f"{self.prefix}/github", github)
        return self

    def write_plaftorm(self):
        platform_sp_client_id = (
            ""
            if "out_tenant_sp_client_id" not in self.data["outputs"]
            else self.data["outputs"]["out_tenant_sp_client_id"]["value"]
        )
        platform_sp_object_id = (
            ""
            if "out_tenant_sp_object_id" not in self.data["outputs"]
            else self.data["outputs"]["out_tenant_sp_object_id"]["value"]
        )
        platform = {
            "app_id": platform_sp_client_id,
            "principal_id": platform_sp_object_id,
            "scope_id": "6332363e-bcba-4c4a-a605-c25f23117400",
        }
        self.upload_config(f"{self.prefix}/platform", platform)
        return self

    def write_powerbi(self):
        powerbi = {
            "scope": "https://analysis.windows.net/powerbi/api/.default",
            "dashboard_view": "",
            "group_id": "",
            "scenario_view": "",
            "workspace.id": "",
            "workspace.name": "",
        }
        self.upload_config(f"{self.prefix}/powerbi", powerbi)
        return self

    def write_webapp(self):
        webapp = {
            "deployment_name": "",
            "enable_insights": False,
            "hostname": "",
            "insights_instrumentation_key": "",
            "location": "",
            "static_domain": "",
        }
        self.upload_config(f"{self.prefix}/webapp", webapp)
        return self
    
    def write_all_config(self):
        self.write_acr()
        self.write_adt()
        self.write_app()
        self.write_adx()
        self.write_api()
        self.write_azure()
        self.write_babylon()
        self.write_github()
        self.write_plaftorm()
        self.write_powerbi()
        self.write_webapp()
        self.set_storage_client_secret()
        self.set_babylon_client_secret()
        return self