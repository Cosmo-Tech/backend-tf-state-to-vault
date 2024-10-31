import logging
import sys
import os
import hvac

logger = logging.getLogger("Babylon")


class DeletePolicies:

    def __init__(self):
        for v in [
                "VAULT_ADDR",
                "VAULT_TOKEN",
        ]:
            if v not in os.environ:
                logger.error(f" {v} is missing")
                sys.exit(1)

        self.server_id = os.environ.get("VAULT_ADDR")
        self.token = os.environ.get("VAULT_TOKEN")

    def delete_policy(self, policy_name):
        client = hvac.Client(url=self.server_id, token=self.token)

        try:
            # Delete the policy
            client.sys.delete_policy(name=policy_name)
            print(f"Policy '{policy_name}' has been deleted.")
        except hvac.exceptions.InvalidRequest as e:
            print(f"Invalid request: {e}")
        except hvac.exceptions.InvalidRequest as e:
            print(f"Policy '{policy_name}' does not exist or could not be deleted: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
