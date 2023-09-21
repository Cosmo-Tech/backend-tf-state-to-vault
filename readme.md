# Platform babylon configuration


* Clone repository
```bash
git clone git@github.com:Cosmo-Tech/backend-tf-state-to-vault.git
```

* Build image

```bash
docker build -t upload .
```

* Run script

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

