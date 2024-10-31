import subprocess
import sys
import json
import os
import logging
import hvac
import re

logger = logging.getLogger("Babylon")


class UserAdd:

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

    def validate_policies(self, policies):
        client = hvac.Client(url=self.server_id, token=self.token)
        existing_policies = client.sys.list_policies()["policies"]

        for policy in policies.split(","):
            if policy not in existing_policies:
                raise ValueError(f"Policy '{policy}' does not exist in Vault.")

    def validate_email(self, email):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            raise ValueError(f"Invalid email address: '{email}'")

    def validate_username(self, username):
        if not username.isalnum():
            raise ValueError(
                f"Username '{username}' contains special characters. Only alphanumeric characters are allowed.")

    def get_accessor(self):
        result = subprocess.run(["vault", "auth", "list", "-format=json"], capture_output=True, text=True)
        auth_list = json.loads(result.stdout)
        accessor = auth_list["userpass-cosmotech/"]["accessor"]
        return accessor

    def create_user(self, username, policies):
        client = hvac.Client(url=self.server_id, token=self.token)
        client.auth.userpass.create_or_update_user(
            username=username,
            password="foo",
            policies=policies,
            mount_point=f"userpass-{self.org_name}",
        )

    def create_entity(self, username, email, team, policies):
        client = hvac.Client(url=self.server_id, token=self.token)
        result = client.secrets.identity.create_or_update_entity(
            name=username,
            policies=policies,
            metadata={
                "organization": self.org_name,
                "team": team,
                "email": email
            },
        )

        # Check if the entity is created and retrieve its ID
        if result:
            entities = client.secrets.identity.list_entities()
            if entities and "data" in entities:
                for entity_id in entities["data"]["keys"]:
                    entity = client.secrets.identity.read_entity(entity_id=entity_id)
                    if entity and "data" in entity and "name" in entity["data"]:
                        if entity["data"]["name"] == username:
                            return entity["data"]["id"]
        else:
            raise ValueError("Unable to retrieve entity ID after creation. Unexpected response structure.")

    def add_user_to_entity(self, username, userid, accessor):
        client = hvac.Client(url=self.server_id, token=self.token)
        client.secrets.identity.create_or_update_entity_alias(name=username,
                                                              canonical_id=userid,
                                                              mount_accessor=accessor)

    def add_user(self, username, email, team, policies):
        # Validate policies, email, and username
        self.validate_policies(policies)
        self.validate_email(email)
        self.validate_username(username)
        self.create_user(username, policies)
        accessor = self.get_accessor()
        print(f"Accessor: {accessor}")
        userid = self.create_entity(username, email, team, policies)
        print(f"Canonical ID: {userid}")
        self.add_user_to_entity(username, userid, accessor)
