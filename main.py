import logging
import argparse
import json
from vault.secrets.add_secrets import AddSecrets
from vault.secrets.delete_secrets import DeletesSecrets
from vault.tenant.enable_tenant import EnableNewTenant
from vault.tenant.disable_tenant import DisableTenant
from vault.user.add_user import UserAdd
from vault.user.delete_user import UserDelete
from vault.policies.add_policies import AddPolicies
from vault.policies.delete_policies import DeletePolicies
from vault.policies.update_policies import UpdatePolicies
from vault.backup_import.backupconfig import Backup
from vault.config.delete_config import DeleteConfig
from vault.config.read_config import ReadConfig
from vault.config.write_config import WriteConfig

logger = logging.getLogger("Babylon")


def main():

    # Create the main parser with a description
    parser = argparse.ArgumentParser(
        description="Script for managing Vault configurations and operations."
    )
    # Add the top-level subcommand (e.g., 'config')
    subparsers = parser.add_subparsers(
        dest="command",
        title="Available Commands",
        metavar="command",
        help="Type of operation to perform",
    )

    # Create the 'config' subcommand parser
    parser_config = subparsers.add_parser(
        "config", help="Operations related to configurations"
    )
    # Create subparsers for the 'config' command
    config_subparsers = parser_config.add_subparsers(
        dest="operation",
        title="Config Operations",
        metavar="operation",
        help='Specific operation to perform under "config"',
    )
    # 'read' subcommand under 'config'
    parser_read = config_subparsers.add_parser("read", help="Read configuration")
    parser_read.add_argument(
        "--resource", help='Specify the resource to read, or "all" for all resources'
    )
    parser_read.add_argument("--file", help="Path to local state file (optional)")
    parser_read.add_argument(
        "--use-azure",
        action="store_true",
        help="Use Azure Blob Storage instead of Vault",
    )
    parser_read.add_argument(
        "--engine",
        help="Specify the version of engine, default: v2",
        choices=["v1", "v2"],
    )

    # 'write' subcommand under 'config'
    parser_write = config_subparsers.add_parser("write", help="Write configuration")
    parser_write.add_argument(
        "--resource", help='Specify the resource to read, or "all" for all resources'
    )
    parser_write.add_argument(
        "--engine",
        help="Specify the version of engine, default: v2",
        choices=["v1", "v2"],
    )
    parser_write.add_argument(
        "--platform-id", required=True, help="Platform ID to delete config"
    )
    parser_write.add_argument("--file", help="Path to local state file (optional)")
    parser_write.add_argument(
        "--use-azure",
        action="store_true",
        help="Use Azure Blob Storage instead of Vault",
    )
    parser_write.add_argument(
        "--from-tfstate",
        action="store_true",
        help="Use terraform state file as data source",
    )

    # 'delete' subcommand under 'config'
    parser_delete = config_subparsers.add_parser(
        "delete", help="delete a new configuration"
    )

    parser_delete.add_argument(
        "--resource",
        required=True,
        help="""
Specify the resource to delete.
Accepted values: "acr", "adx ..", or "All" to delete configuration for all resources.
""",
    )
    parser_delete.add_argument(
        "--engine",
        help="Specify the version of engine, default: v2",
        choices=["v1", "v2"],
    )
    parser_delete.add_argument(
        "--platform-id", required=True, help="Platform ID to delete config"
    )

    # 'destroy' subcommand under 'config'
    parser_destroy = config_subparsers.add_parser(
        "destroy", help="destroy a new configuration"
    )

    parser_destroy.add_argument(
        "--resource",
        required=True,
        help="""
Specify the resource to delete. 
Accepted values: "acr", "adx ..", or "All" to delete configuration for all resources.',
""",
    )
    parser_destroy.add_argument(
        "--platform-id", required=True, help="Platform ID to delete config"
    )

    # Create the 'tenant' subcommand parser
    parser_tenant = subparsers.add_parser("tenant", help="Operations related to Tenant")
    tenant_subparsers = parser_tenant.add_subparsers(
        dest="operation",
        title="Available operation",
        metavar="operation",
        help="Describe of operation to perform",
    )

    enable_parser = tenant_subparsers.add_parser("enable", help="Enable a new tenant")
    enable_parser.add_argument(
        "--name", required=True, help="Secret engine name / mount"
    )
    enable_parser.add_argument(
        "--engine",
        help="Specify the version of engine, default: v2",
        choices=["v1", "v2"],
    )
    disable_parser = tenant_subparsers.add_parser(
        "disable", help="Disable an existing tenant"
    )
    disable_parser.add_argument(
        "--name", required=True, help="Secret engine name / mount"
    )

    # Add the 'User' subcommand parserimport pathlib
    parser_adduser = subparsers.add_parser("add", help="Add a new user")
    user_subparsers = parser_adduser.add_subparsers(
        dest="operation",
        title="Available operations",
        metavar="operation",
        help="Description of the operation to perform",
    )

    # 'adduser' subcommand under 'user'
    parser_adduser.add_argument(
        "--username", required=True, help="Username for the adduser operation"
    )
    parser_adduser.add_argument(
        "--email", required=True, help="Email for the adduser operation"
    )
    parser_adduser.add_argument(
        "--team", required=True, help="Team for the adduser operation"
    )
    parser_adduser.add_argument(
        "--policies", required=True, help="Policies for the adduser operation"
    )

    # 'userdelete' subcommand under 'user'
    parser_userdelete = user_subparsers.add_parser(
        "delete", help="Delete an existing user"
    )
    parser_userdelete.add_argument(
        "--username", required=True, help="Username of the user to delete"
    )

    parser_secrets = subparsers.add_parser(
        "secrets", help="Operations related to secrets management"
    )

    secret_subparsers = parser_secrets.add_subparsers(
        dest="operation",
        title="Available operations",
        metavar="operation",
        help="Description of the operation to perform",
    )

    parser_addsecrets = secret_subparsers.add_parser("add", help="Add a new secret")
    parser_addsecrets.add_argument(
        "--secrets-path",
        required=True,
        help="Path to the Json file containing secrets platform",
    )
    secret_subparsers.add_parser("delete", help="Delete an existing secret")

    # Add the 'policies' subcommand parser
    parser_policies = subparsers.add_parser(
        "policies", help="Operations related to policies management"
    )

    # Define subparsers for different policy operations
    policies_subparsers = parser_policies.add_subparsers(
        dest="operation",
        title="Available operations",
        metavar="operation",
        help="Description of the operation to perform",
    )

    # 'add' subcommand under 'policies'
    parser_addpolicies = policies_subparsers.add_parser("add", help="Add a new policy")
    parser_addpolicies.add_argument(
        "--policy-file",
        required=True,
        help="Path to the YAML file containing policy definitions",
    )

    # 'delete' subcommand under 'policies'
    parser_deletepolicies = policies_subparsers.add_parser(
        "delete", help="Delete an existing policy"
    )
    parser_deletepolicies.add_argument(
        "--policy-name", required=True, help="Name of the policy to delete"
    )
    # 'upadte' subcommand under 'policies'
    parser_updatepolicies = policies_subparsers.add_parser(
        "update", help="update an existing policy"
    )
    parser_updatepolicies.add_argument(
        "--policy-file",
        required=True,
        help="Path to the YAML file containing update policy definitions",
    )

    # Add the 'data' subcommand parser
    parser_data = subparsers.add_parser(
        "data",  # Use lowercase for command names
        help="Operations related to data management",
    )

    # Define subparsers for different data operations
    data_subparsers = parser_data.add_subparsers(
        dest="operation",
        title="Available operations",
        metavar="operation",
        help="Description of the operation to perform",
    )

    # 'backup' subcommand under 'data'
    # parser_backup = data_subparsers.add_parser("backup", help="Backup data config")
    parser_backup = data_subparsers.add_parser(
        name="backup",
        help="save config data in a local file named backup.<platform-id>.json",
    )
    parser_backup.add_argument(
        "--engine",
        help="Specify the version of engine, default: v2",
        choices=["v1", "v2"],
    )
    parser_backup.add_argument(
        "--platform-id", required=True, help="Platform ID containing all secrets"
    )

    # Parse the arguments
    args = parser.parse_args()

    disable = DisableTenant()
    useradd = UserAdd()
    userdelete = UserDelete()
    secretsadd = AddSecrets()
    secretsdelete = DeletesSecrets()
    addpolicies = AddPolicies()
    deletepolicies = DeletePolicies()
    updatepolicies = UpdatePolicies()

    # Handling the commands
    if args.command == "config":
        if args.operation == "write":
            try:
                write = WriteConfig(
                    version_engine=args.engine,
                    local_file=args.file,
                    use_azure=args.use_azure,
                    from_tfstate=args.from_tfstate,
                )
                print("Writing configuration for all resources.")
                if args.resource == "all":
                    write.write_all_config(platform_id=args.platform_id)
                else:
                    write.write_config(
                        resource=args.resource, platform_id=args.platform_id
                    )
                print("Configuration written successfully.")
            except Exception as e:
                print(f"An error occurred while writing the configuration: {str(e)}")
        elif args.operation == "read":
            if not args.resource:
                logger.error(
                    "Error: --resource is required. Use 'all' to read all resources or specify a specific resource."
                )
                parser_read.print_help()
            else:
                try:
                    logger.info(
                        f"Initializing ReadConfig with file={args.file}, use_azure={args.use_azure}"
                    )
                    read = ReadConfig(
                        local_file=args.file,
                        use_azure=args.use_azure,
                        version_engine=args.engine,
                    )
                    if args.resource == "all":
                        logger.info("Reading configuration for all resources.")
                        config = read.read_all_config()
                    else:
                        logger.info(
                            f"Reading configuration for resource: {args.resource}"
                        )
                        config = read.get_config(args.resource)

                    if config:
                        print(json.dumps(config, indent=2))
                    else:
                        logger.warning(
                            f"No configuration found for resource: {args.resource}"
                        )
                except Exception as e:
                    logger.error(
                        f"An error occurred while reading the configuration: {str(e)}",
                        exc_info=True,
                    )
        elif args.operation == "delete":
            delete = DeleteConfig(version_engine=args.engine)
            if args.resource == "all":
                if args.platform_id:
                    print("Deleting configuration for all resources.")
                    delete.delete_all_config(args.platform_id)
                else:
                    print("Error: --platform_id is required when --resource is 'All'.")
                    parser_delete.print_help()
            else:
                if args.platform_id:
                    print(f"Deleting configuration for resource: {args.resource}")
                    delete.delete_get_config(args.resource, args.platform_id)
                else:
                    print(
                        "Error: --platform_id is required when deleting a specific resource."
                    )
                    parser_delete.print_help()
        elif args.operation == "read":
            if args.resource == "all":
                print("Reading configuration for all resources.")
                # read.read_all_config()
        else:
            parser_config.print_help()
    elif args.command == "tenant":
        enable = EnableNewTenant(version_engine=args.engine)
        if args.operation == "enable":
            print("Enabling a new secret engine.")
            enable.enable(secret_engine=args.name)
        elif args.operation == "disable":
            print("Disabling a secret engine.")
            disable.disable(secret_engine=args.name)
        else:
            parser_tenant.print_help()
    elif args.command == "user":
        if args.operation == "add":
            if args.username and args.email and args.team and args.policies:
                print("adding a new user")
                useradd.add_user(args.username, args.email, args.team, args.policies)
            else:
                print("Error: Missing required arguments for adding a user.")
                # parser_adduser.print_help()
        elif args.operation == "delete":
            if args.username:
                print("deleting a user")
                userdelete.delete_user(args.username)
            else:
                print(
                    "Error: Missing required argument '--username' for deleting a user."
                )
                # parser_userdelete.print_help()
        # else:
        # parser_user.print_help()
    elif args.command == "secrets":
        if args.operation == "add":
            if args.secrets_path:
                print("Adding Platform secrets.")
                secretsadd.add_patform_secrets(args.secrets_path)
            else:
                print("Error: --secrets_path argument is required for adding secrets.")
                parser_addsecrets.print_help()
        elif args.operation == "delete":
            print("Deleting Platform secrets.")
            secretsdelete.delete_secrets()
        else:
            parser_secrets.print_help()
    elif args.command == "policies":
        if args.operation == "add":
            if not args.policy_file:
                print("Error: --policy-file argument is required for adding policies.")
                parser_addpolicies.print_help()
            else:
                print(f"Adding policies from file: {args.policy_file}.")
                addpolicies.add_policies_from_file(args.policy_file)
        elif args.operation == "delete":
            if not args.policy_name:
                print(
                    "Error: --policy-name argument is required for deleting policies."
                )
                parser_deletepolicies.print_help()
            else:
                print(f"Deleting policy: {args.policy_name}.")
                deletepolicies.delete_policy(args.policy_name)
        elif args.operation == "update":
            if not args.policy_file:
                print(
                    "Error: --policy-file argument is required for updating policies."
                )
                parser_deletepolicies.print_help()
            else:
                print(f"Updating policy: {args.policy_file}.")
                updatepolicies.update_policies_from_file(args.policy_file)
        else:
            parser_policies.print_help()
    elif args.command == "data":
        backup = Backup(version_engine=args.engine)
        if args.operation == "backup":
            print("Backing up data config.")
            backup.backup_config(platform_id=args.platform_id)
        else:
            parser_data.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
