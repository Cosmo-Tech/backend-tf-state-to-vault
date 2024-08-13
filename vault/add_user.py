import subprocess
import sys
import json
import os
import logging
from hvac import Client

logger = logging.getLogger("Babylon")


class UserOperations:
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

    def get_accessor(self):
        result = subprocess.run(['vault', 'auth', 'list', '-format=json'], capture_output=True, text=True)
        auth_list = json.loads(result.stdout)
        accessor = auth_list["userpass-cosmotech/"]["accessor"]
        return accessor

    def create_user(self, username, policies):
        client = Client(url=self.server_id, token=self.token)
        client.write(f'auth/userpass-cosmotech/users/{username}', password='foo', policies=policies)

    def create_entity(self, username, email, team, policies):
        client = Client(url=self.server_id, token=self.token)
        result = client.write('identity/entity', name=username, policies=policies, 
                            metadata={
                                'organization': self.org_name, 
                                'team': team, 
                                'email': email
                            })
        if result:
            entities = client.list('identity/entity/id')
            if entities and 'data' in entities:
                for entity_id in entities['data']['keys']:
                    entity = client.read(f'identity/entity/id/{entity_id}')
                    if entity and 'data' in entity and 'id' in entity['data']:
                        if entity['data']['name'] == username:
                            return entity['data']['id']
            raise ValueError("Unable to retrieve entity ID after creation.")
        else:
            raise ValueError("Unexpected response structure: " + str(result))
    
    def add_user_to_entity(self, username, userid, accessor):
        client = Client(url=self.server_id, token=self.token)
        client.write('identity/entity-alias', name=username, canonical_id=userid, mount_accessor=accessor)

    def adduser(self, username, email, team, policies):
        self.create_user(username, policies)
        accessor = self.get_accessor()
        print(f'Accessor : {accessor}')
        userid = self.create_entity(username, email, team, policies)
        print(f'Canonical_id : {userid}')
        self.add_user_to_entity(username, userid, accessor)


