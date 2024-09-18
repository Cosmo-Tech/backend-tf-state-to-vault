import logging
import sys
import os
import hvac
import yaml

logger = logging.getLogger("Babylon")


class AddPolicies:

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

    def add_policies_from_file(self, file_path):
        client = hvac.Client(url=self.server_id, token=self.token)
        """
        Adds policies to Vault from a YAML file.

        :param file_path: Path to the YAML file containing policies
        """
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            return

        try:
            with open(file_path, 'r') as f:
                policies = yaml.safe_load(f)

            if not isinstance(policies, dict):
                raise ValueError("YAML file must contain a dictionary of policies.")

            for policy_name, policy_rules in policies.items():
                if not policy_name or not policy_rules:
                    print(f"Skipping invalid policy: {policy_name}")
                    continue
                # Check if the policy already exists
                try:
                    existing_policy = client.sys.read_policy(name=policy_name)
                    if existing_policy:
                        print(f"Policy '{policy_name}' already exists. Skipping creation.")
                        continue
                except hvac.exceptions.InvalidPath:
                    # If the policy does not exist, an InvalidPath exception is raised.
                    print(f"Policy '{policy_name}' does not exist. Creating new policy.")

                # Add or update the policy in Vault
                client.sys.create_or_update_policy(name=policy_name, policy=policy_rules)
                print(f"Policy '{policy_name}' has been added or updated successfully.")

        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")

        except hvac.exceptions.InvalidRequest as e:
            print(f"Error adding policy: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")
