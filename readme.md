### Configuring Initialization Variables in Babylon Vault

The first step is to retrieve the Docker image:

```bash
docker pull ghcr.io/cosmo-tech/backend-tf-state-to-vault:<version>
docker tag ghcr.io/cosmo-tech/backend-tf-state-to-vault:<version> upload
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
        "acr_login_server": {
            "value": <value>
        },
        "adx_uri": {
            "value": <value>
        },
        "cluster_principal_id": {
            "value": <value>
        },
        "cosmos_api_url": {
            "value": <value>
        },
        "cosmos_api_version": {
            "value": "v2"
        },
        "resource_group_name": {
            "value": <value>
        },
        "resource_location": {
            "value": <value>
        },
        "storage_account_name": {
            "value": <value>
        },
        "storage_account_secret": {
            "value": <value>
        },
        "babylon_client_id": {
            "value": <value>
        },
        "babylon_principal_id": {
            "value": <value>
        },
        "babylon_client_secret": {
            "value": <value>
        },
        "platform_sp_client_id": {
            "value": <value>
        },
        "platform_sp_object_id": {
            "value": <value>
        },
        "subscription_id": {
            "value": <value>
        }
    }
}
```

Below, the meaning and role of each of the defined values above are detailed:

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
