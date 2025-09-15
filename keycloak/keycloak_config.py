import requests
import json
import os
from typing import Dict, Optional
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_config() -> Dict[str, Optional[str]]:
    """Load configuration directly from environment variables"""
    required_vars = [
        'KEYCLOAK_URL', 'REALM', 'CLIENT_NAME', 'ADMIN_REALM', 'SCOPE',
        'KEYCLOAK_ADMIN', 'KEYCLOAK_ADMIN_PASSWORD'
    ]

    config = {var: os.getenv(var) for var in required_vars}

    if None in config.values():
        missing = [k for k, v in config.items() if v is None]
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    
    return config

def get_admin_token(config: Dict[str, str]) -> str:
    """Retrieve the administration token"""
    token_url = f"{config['KEYCLOAK_URL']}/realms/{config['ADMIN_REALM']}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": config["KEYCLOAK_ADMIN"],
        "password": config["KEYCLOAK_ADMIN_PASSWORD"]
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_client_credentials(config: Dict[str, str], token: str) -> Dict[str, str]:
    """Retrieve the credentials of the specified client"""
    clients_url = f"{config['KEYCLOAK_URL']}/admin/realms/{config['REALM']}/clients?clientId={config['CLIENT_NAME']}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(clients_url, headers=headers)
    response.raise_for_status()
    clients = response.json()
    
    if not clients:
        raise ValueError(f"Client '{config['CLIENT_NAME']}' introuvable dans le realm '{config['REALM']}'")
    
    client_id = clients[0]["id"]
    
    secret_url = f"{config['KEYCLOAK_URL']}/admin/realms/{config['REALM']}/clients/{client_id}/client-secret"
    response = requests.get(secret_url, headers=headers)
    response.raise_for_status()
    
    return {
        "client_id": config["CLIENT_NAME"],
        "client_secret": response.json().get("value"),
        "token_url": f"{config['KEYCLOAK_URL']}/realms/{config['REALM']}/protocol/openid-connect/token",
        "scope": config["SCOPE"]
    }


def save_keycloak_vault_config(content, file_path):
    """Save keycloak vault config content to a file"""
    with open(file_path, "w") as f:
        json.dump(content, f, indent=4)

def main():
    config_directory = Path.home() / "keycloak_vault_config"
    config_directory.mkdir(parents=True, exist_ok=True)
    try:
        config = load_config()
        
        token = get_admin_token(config)

        credentials = get_client_credentials(config, token)
        
        output = {
            "url": credentials["token_url"],
            "grant_type": "client_credentials",
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "scope": credentials["scope"]
        }
        config_path = config_directory / "client_credentials.json"
        save_keycloak_vault_config(output, config_path)
        logging.info(f"Configuration saved in {config_path}")

    except Exception as e:
        logging.error(f"Erreur: {str(e)}")

if __name__ == "__main__":
    main()