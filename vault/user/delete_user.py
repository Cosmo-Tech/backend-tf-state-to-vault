import sys
import os
import logging
import hvac

logger = logging.getLogger("Babylon")


class UserDelete:

    def __init__(self):
        for v in [
                "VAULT_ADDR",
                "VAULT_TOKEN",
                "ORGANIZATION_NAME",
        ]:
            if v not in os.environ:
                logger.error(f" {v} is missing")
                sys.exit(1)

        self.server_id = os.environ.get("VAULT_ADDR")
        self.token = os.environ.get("VAULT_TOKEN")
        self.org_name = os.environ.get("ORGANIZATION_NAME")

    def user_exists(self, username):
        client = hvac.Client(url=self.server_id, token=self.token)

        # Check if user exists in userpass authentication method
        try:
            try:
                client.auth.userpass.read_user(username, mount_point=f"userpass-{self.org_name}")
                userpass_exists = True
            except hvac.exceptions.InvalidRequest:
                userpass_exists = False

            # Check if user exists in identity engine
            identity_exists = False
            entities = client.secrets.identity.list_entities()
            if entities and "data" in entities:
                for eid in entities["data"]["keys"]:
                    entity = client.secrets.identity.read_entity(entity_id=eid)
                    if entity and "data" in entity:
                        if entity["data"]["name"] == username:
                            identity_exists = True
                            break

            return userpass_exists or identity_exists

        except hvac.exceptions.InvalidRequest as e:
            print(f"Error checking user existence: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def delete_user(self, username):
        client = hvac.Client(url=self.server_id, token=self.token)

        if self.user_exists(username):
            # Delete the user from the userpass auth method
            try:
                client.auth.userpass.delete_user(username, mount_point=f"userpass-{self.org_name}")
                print(f'User "{username}" has been deleted from the userpass authentication method.')
            except hvac.exceptions.InvalidRequest:
                print(f'User "{username}" not found in userpass authentication method.')

            # Retrieve and delete the associated identity entity and alias
            entities = client.secrets.identity.list_entities()
            entity_id = None
            if entities and "data" in entities:
                for eid in entities["data"]["keys"]:
                    entity = client.secrets.identity.read_entity(entity_id=eid)
                    if entity and "data" in entity:
                        if entity["data"]["name"] == username:
                            entity_id = eid
                            break

            if entity_id:
                # Delete any aliases associated with the entity
                aliases = client.secrets.identity.list_entity_aliases()
                if aliases and "data" in aliases:
                    for alias_id in aliases["data"]["keys"]:
                        alias = client.secrets.identity.read_entity_alias(alias_id=alias_id)
                        if alias and "data" in alias:
                            if alias["data"]["canonical_id"] == entity_id:
                                client.secrets.identity.delete_entity_alias(alias_id=alias_id)
                                print("""
Alias "{alias["data"]["name"]}" associated with user "{username}" has been deleted.
""")

                # Delete the entity itself
                client.secrets.identity.delete_entity(entity_id=entity_id)
                print(f'Entity associated with user "{username}" has been deleted.')

            else:
                print(f'No identity entity found for user "{username}".')
