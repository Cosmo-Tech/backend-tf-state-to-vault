### Configuring Initialization Variables in Babylon Vault

The first step is to retrieve the Docker image:

```bash
docker pull ghcr.io/cosmo-tech/backend-tf-state-to-vault:latest
```

Next, you will need to run the Docker image. However, it is necessary to set the following environment variables beforehand:

```bash
export VAULT_ADDR=<value>
export VAULT_TOKEN=<value>
export TENANT_ID=<value>
export ORGANIZATION_NAME=<value>
export CLUSTER_NAME=<value>
export STORAGE_ACCOUNT_NAME=
export STORAGE_ACCOUNT_KEY=
export STORAGE_CONTAINER=
export TFSTATE_BLOB_NAME=
export PLATFORM_NAME=<value>
```

- `TENANT_ID` should correspond to the Microsoft Enterprise ID tenant identifier on which you wish to deploy resources. This value is used for the secrets' storage hierarchy in Vault: `secrets/[organization_name]/[tenant_id]/`.
- `ORGANIZATION_NAME` is used for the secrets' storage hierarchy in Vault: `secrets/[organization_name]/`.
- `STORAGE_ACCOUNT_NAME` and the following three variables can remain empty, as they are managed automatically by the latest available Terraform scripts.
- `PLATFORM_NAME`: the name of the platform, which will be passed as a parameter to Babylon commands via the `-p` option. In the Vault hierarchy, this implies `secrets/[organization_name]/[tenant_id]/[Platform_name]/`.
- `CLUSTER_NAME` is the name of the Kubernetes cluster. This value is used for the secrets hierarchy in Vault: `secrets/[organization_name]/[tenant_id]/clusters/[cluster_name]/`.

If you have a terraform state file in azure storage account.
```bash
docker run -it \
 -e VAULT_ADDR="$VAULT_ADDR" \
 -e VAULT_TOKEN="$VAULT_TOKEN" \
 -e TENANT_ID="$TENANT_ID" \
 -e ORGANIZATION_NAME="$ORGANIZATION_NAME" \
 -e CLUSTER_NAME="$CLUSTER_NAME" \
 -e STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
 -e STORAGE_ACCOUNT_KEY="$STORAGE_ACCOUNT_KEY" \
 -e STORAGE_CONTAINER="$STORAGE_CONTAINER" \
 -e TFSTATE_BLOB_NAME="$TFSTATE_BLOB_NAME" \
 -e PLATFORM_NAME="$PLATFORM_NAME" ghcr.io/cosmo-tech/backend-tf-state-to-vault
```

If you don't have a terraform state file in azure storage account but locally, copy the following content into the `state.json` file and configure it correctly:

```json
{
    "outputs": {
        "out_acr_login_server": {
            "value": "",
        },
        "out_adx_uri": {
            "value": "",
        },
        "out_babylon_client_id": {
            "value": "",
        },
        "out_babylon_client_secret": {
            "value": "",
        },
        "out_babylon_principal_id": {
            "value": "",
        },
        "out_cluster_adx_name": {
            "value": "",
        },
        "out_cluster_adx_principal_id": {
           "value": "",
        },
        "out_cosmos_api_scope": {
            "value": "",
        },
        "out_cosmos_api_url": {
            "value": "",
        },
        "out_cosmos_api_version_path": {
            "value": "",
        },
        "out_resource_location": {
            "value": "",
        },
        "out_storage_account_name": {
            "value": "",
        },
        "out_storage_account_secret": {
            "value": "",
        },
        "out_subscription_id": {
            "value": "",
        },
        "out_tenant_resource_group_name": {
            "value": "",
        },
        "out_tenant_sp_client_id": {
            "value": "",
        },
        "out_tenant_sp_object_id": {
            "value": "",
        }
    }
}
```
- `acr_login_server`: Docker image server where the simulator image is located (refer to the resource group of the platform).
- `adx_uri`: URI of the ADX cluster in the same resource group.
- `cluster_principal_id`: Principal identifier of the ADX cluster (to be retrieved from its JSON view).
- `cosmos_api_url`: URL of the API as previously deployed via Terraform scripts.
- `cosmos_api_version`: `v3` API version that will be concatenated with `cosmos_api_url` to obtain the complete URL to use.
- `resource-group-name`: The resource group.
- `resource_location`: Region in which the resource group is deployed: e.g `westeurope`.
- `storage_account_name`: get the name of the storage account of the platform resource group.
- `storage_account_secret`: go to the `Access Key` menu and use `key1`.
- `babylon_client_id`: retrieve the application ID from the enterprise application of `Babylon`
- `babylon_principal_id`: retrieve the object ID from the enterprise application `Babylon`
- `babylon_client_secret`: create a new secret in the enterprise application `Babylon`

For the secrets, you should have this JSON file locally with the name `secrets.json`, which can be used to populate Vault with those secrets : 
```json
{
    "outputs": {
        "out_API_VERSION": {
            "value": ""
        },
        "out_ACR_SERVER": {
            "value": ""
        },
        "out_ACR_USERNAME": {
            "value": ""
        },
        "out_ACR_PASSWORD": {
            "value": ""
        },
        "out_ACR_REGISTRY_URL": {
            "value": ""
        },
        "out_HOST_COSMOTECH_API": {
            "value": ""
        },
        "out_IDENTITY_AUTHORIZATION_URL": {
            "value": ""
        },
        "out_IDENTITY_TOKEN_URL": {
            "value": ""
        },
        "out_MONITORING_NAMESPACE": {
            "value": ""
        },
        "out_NAMESPACE": {
            "value": ""
        },
        "out_ARGO_SERVICE_ACCOUNT_NAME": {
            "value": ""
        },
        "out_AZURE_TENANT_ID": {
            "value": ""
        },
        "out_AZURE_APPID_URI": {
            "value": ""
        },
        "out_AZURE_STORAGE_ACCOUNT_KEY": {
            "value": ""
        },
        "out_AZURE_STORAGE_ACCOUNT_NAME": {
            "value": ""
        },
        "out_AZURE_CREDENTIALS_CLIENT_ID": {
            "value": ""
        },
        "out_AZURE_CREDENTIALS_CLIENT_SECRET": {
            "value": ""
        },
        "out_AZURE_CREDENTIALS_CUSTOMER_CLIENT_ID": {
            "value": ""
        },
        "out_AZURE_CREDENTIALS_CUSTOMER_CLIENT_SECRET": {
            "value": ""
        },
        "out_ADX_BASE_URI": {
            "value": ""
        },
        "out_ADX_INGEST_URI": {
            "value": ""
        },
        "out_EVENTBUS_BASE_URI": {
            "value": ""
        },
        "out_HOST_POSTGRES": {
            "value": ""
        },
        "out_HOST_REDIS": {
            "value": ""
        },
        "out_HOST_REDIS_PASSWORD": {
            "value": ""
        },
        "out_HOST_ARGO_WORKFLOWS_SERVER": {
            "value": ""
        },
        "out_RDS_HUB_LISTENER": {
            "value": ""
        },
        "out_RDS_HUB_SENDER": {
            "value": ""
        },
        "out_RDS_STORAGE_ADMIN": {
            "value": ""
        },
        "out_RDS_STORAGE_READER": {
            "value": ""
        },
        "out_RDS_STORAGE_WRITER": {
            "value": ""
        },
        "out_HOST_RDS": {
            "value": ""
        },
        "out_HOST_RDS_POSTGRES": {
            "value": ""
        },
        "out_SPRING_APPLICATION_JSON": {
            "value": ""
        }
    }
}
```
Below, the meaning and role of each of the defined values above are detailed:
```bash
docker run -it --entrypoint bash \ 
 -e VAULT_ADDR="$VAULT_ADDR" \
 -e VAULT_TOKEN="$VAULT_TOKEN" \
 -e TENANT_ID="$TENANT_ID" \
 -e ORGANIZATION_NAME="$ORGANIZATION_NAME" \
 -e CLUSTER_NAME="$CLUSTER_NAME" \
 -e STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
 -e STORAGE_ACCOUNT_KEY="$STORAGE_ACCOUNT_KEY" \
 -e STORAGE_CONTAINER="$STORAGE_CONTAINER" \
 -e TFSTATE_BLOB_NAME="$TFSTATE_BLOB_NAME" \
 -e PLATFORM_NAME="$PLATFORM_NAME" \
 -v <path>/<state.json>:/usr/src/babyapp/state.json \
 -v <path>/<secrets.json>:/usr/src/babyapp/secrets.json ghcr.io/cosmo-tech/backend-tf-state-to-vault
```
With `--entrypoint bash`, you can enter interactive mode to execute all commands within the Python application. Here's what the application looks like:

![alt text](image.png)

## Function : 
- `addtenant`: Enables a new secrets engine.
- `addpolicies`: Adds policies for admin, contributor, user, and external roles.
- `addsecret`: Adds secrets defined in the secrets.json file.
- `writeconfig`: Writes the entire platform configuration.
- `deleteconfig`: Deletes the entire platform configuration.
- `backup`: Creates a backup of the configuration for the current platform ID, which is specified in the platform_name environment variable. The backup is saved as a JSON file named `backup-<platform_name>.json`.
- `import`: Imports the configuration for a platform and applies it to another platform. This function takes a parameter named `platform_id_to`, which specifies the target platform ID.
- `adduser`: Adds a new user. This function requires parameters for user details.
- `readconfig`: Reads a specific configuration.




