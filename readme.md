### Configuring Initialization Variables in Babylon Vault

The first step is to retrieve the Docker image:

```bash
docker pull ghcr.io/cosmo-tech/backend-tf-state-to-vault:latest
docker tag ghcr.io/cosmo-tech/backend-tf-state-to-vault:latest upload
```

Next, you will need to run the Docker image. However, it is necessary to set the following environment variables beforehand:

```bash
export VAULT_ADDR=<value>
export VAULT_TOKEN=<value>
export TENANT_ID=<value>
export ORGANIZATION_NAME=<value>
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

Then, copy the following content into the `state.json` file and configure it correctly:

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

Below, the meaning and role of each of the defined values above are detailed:
```bash
docker run -it \
 -e VAULT_ADDR="$VAULT_ADDR" \
 -e VAULT_TOKEN="$VAULT_TOKEN" \
 -e TENANT_ID="$TENANT_ID" \
 -e ORGANIZATION_NAME="$ORGANIZATION_NAME" \
 -e STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT_NAME" \
 -e STORAGE_ACCOUNT_KEY="$STORAGE_ACCOUNT_KEY" \
 -e STORAGE_CONTAINER="$STORAGE_CONTAINER" \
 -e TFSTATE_BLOB_NAME="$TFSTATE_BLOB_NAME" \
 -e PLATFORM_NAME="$PLATFORM_NAME" \
 -v <path>/terraform.tfstate:/usr/src/babyapp/state.json upload
```


- `acr_login_server`: Docker image server where the simulator image is located (refer to the resource group of the platform).
- `adx_uri`: URI of the ADX cluster in the same resource group.
- `cluster_principal_id`: Principal identifier of the ADX cluster (to be retrieved from its JSON view).
- `cosmos_api_url`: URL of the API as previously deployed via Terraform scripts.
- `cosmos_api_version`: `v2` API version that will be concatenated with `cosmos_api_url` to obtain the complete URL to use.
- `resource-group-name`: The resource group.
- `resource_location`: Region in which the resource group is deployed: e.g `West Europe`.
- `storage_account_name`: get the name of the storage account of the platform resource group.
- `storage_account_secret`: go to the `Access Key` menu and use `key1`.
- `babylon_client_id`: retrieve the application ID from the enterprise application of `Babylon`
- `babylon_principal_id`: retrieve the object ID from the enterprise application `Babylon`
- `babylon_client_secret`: create a new secret in the enterprise application `Babylon`
