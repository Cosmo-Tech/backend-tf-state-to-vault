import logging
import argparse
from vault.add_secrects import ExtractSecrets
from vault.enable_tenant import EnableNewTenant
from vault.write_config import ExtractConfig
from vault.add_user import UserOperations
from vault.add_policies import AddPlocies
from vault.backupconfig import BackupConfig
from vault.importconfig import ImportConfig
from vault.delete_config import DeletConfig
from vault.read_config import ReadConfig

logger = logging.getLogger("Babylon")

def main():
    parser = argparse.ArgumentParser(description='Vault Operations Script')
    subparsers = parser.add_subparsers(dest='operation', help='Operation to perform')

    parser_addtenant = subparsers.add_parser('addtenant', help='Enable a new tenant')
    parser_addpolicies = subparsers.add_parser('addpolicies', help='Create policies')
    parser_addsecret = subparsers.add_parser('addsecret', help='Add platform secrets')
    parser_writeconfig = subparsers.add_parser('writeconfig', help='Write various configurations')
    parser_deleteconfig = subparsers.add_parser('deleteconfig', help='Delete various configurations')
    parser_backup = subparsers.add_parser('backup', help='Backup configuration for a specific platform')
    parser_import = subparsers.add_parser('import', help='Import configuration from to a specific platform')
    parser_adduser = subparsers.add_parser('adduser', help='Add a new user')
    parser_readconfig = subparsers.add_parser('readconfig', help='read various configurations')

    parser_readconfig.add_argument('--resources', required=True, help='The resources should include acr, adt, adx....')
    #parser_import.add_argument('--platform_id_from', required=True, help='Platform ID from importing config')
    parser_import.add_argument('--platform_id_to', required=True, help='Platform ID to importing config')

    parser_deleteconfig.add_argument('--platform_id', required=True, help='Platform ID to delete config')

    #parser_backup.add_argument('--platform_id', required=True, help='Platform ID from importing config')
    parser_adduser.add_argument('--username', required=True, help='Username for the adduser operation')
    parser_adduser.add_argument('--email', required=True, help='Email for the adduser operation')
    parser_adduser.add_argument('--team', required=True, help='Team for the adduser operation')
    parser_adduser.add_argument('--policies', required=True, help='Policies for the adduser operation')
    args = parser.parse_args()

    secrets = ExtractSecrets()
    tenants = EnableNewTenant()
    write_config = ExtractConfig()
    users = UserOperations()
    policies = AddPlocies()
    config_backup = BackupConfig()
    config_import = ImportConfig()
    delete_config = DeletConfig()
    read_config = ReadConfig()

    if args.operation == 'addtenant':
        tenants.enable_tenant()
    elif args.operation == 'addpolicies':
        policies.create_policies()
    elif args.operation == 'addsecret':
        secrets.add_patform_secrets()
    elif args.operation == 'writeconfig':
        write_config.write_all_config()
        write_config.set_babylon_client_secret().set_storage_client_secret()
    elif args.operation == 'deleteconfig':
        delete_config.delete_all_config(args.platform_id)
        delete_config.delete_babylon_client_secret().delete_storage_client_secret()
    elif args.operation == 'readconfig':
        read_config.get_config(args.resources)
    elif args.operation == 'backup':
        config_backup.backup_config()
        #config_backup.save_backup_to_blob()
    elif args.operation == 'import':
        config_import.import_config(args.platform_id_to)
    elif args.operation == 'adduser':
        users.adduser(args.username, args.email, args.team, args.policies)
    else:
        logger.error("Invalid operation specified")

if __name__ == "__main__":
    main()
