# Platform babylon configuration


* Pull and tag
```bash
docker pull ghcr.io/cosmo-tech/backend-tf-state-to-vault:latest
docker tag ghcr.io/cosmo-tech/backend-tf-state-to-vault:latest upload
```

* Run script

```bash
export VAULT_ADDR=
export VAULT_TOKEN=
export TENANT_ID=
export ORGANIZATION_NAME=
export STORAGE_ACCOUNT_NAME=
export STORAGE_ACCOUNT_KEY=
export STORAGE_CONTAINER=
export TFSTATE_BLOB_NAME=
export PLATFORM_NAME=
```

Option 1. script terraform.

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
 -e PLATFORM_NAME="$PLATFORM_NAME" upload
```

Option 2. script local

* If you have a local tfstate json file 

```json
{
    "outputs": {
        "acr_login_server": {
            "value": ""
        },
        "adx_uri": {
            "value": ""
        },
        "cluster_principal_id": {
            "value": ""
        },
        "cosmos_api_url": {
            "value": ""
        },
        "resource_group_name": {
            "value": ""
        },
        "resource_location": {
            "value": ""
        },
        "storage_account_name": {
            "value": ""
        },
        "storage_account_secret": {
            "value": ""
        },
        "babylon_client_id": {
            "value": ""
        },
        "babylon_principal_id": {
            "value": ""
        },
        "babylon_client_secret": {
            "value": ""
        },
        "platform_sp_client_id": {
            "value": ""
        },
        "platform_sp_object_id": {
            "value": ""
        },
        "subscription_id": {
            "value": ""
        }
    }
}
```

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
 -v ./path/state.json:/usr/src/babyapp/state.json upload
```


