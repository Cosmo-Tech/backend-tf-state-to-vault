#!/usr/bin/env bash
# =============================================================================
# Run Keycloak + Vault configuration with environment setup
#
# Usage:
#   ./run-config.sh <venv> <platform> <tenant>
#
# Example:
#   ./run-config.sh backend-vault-env dev sphinx
# =============================================================================

set -euo pipefail

# --- Helpers ---------------------------------------------------------------
print_section() {
    echo -e "\n\033[1;34m==> $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✔ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m✘ $1\033[0m"
}

# --- Argument check --------------------------------------------------------
if [[ $# -ne 3 ]]; then
    print_error "Usage: $0 <venv> <platform> <tenant>"
    exit 1
fi

PY_VENV="$1"
platform="$2"
tenant="$3"

# --- Virtualenv activation -------------------------------------------------
VENV_PATH="${HOME}/${PY_VENV}/bin/activate"
print_section "Activating virtual environment: $PY_VENV"
if [[ -f "$VENV_PATH" ]]; then
    source "$VENV_PATH"
    print_success "Virtual environment activated"
else
    print_error "Virtual environment not found at $VENV_PATH"
    exit 1
fi

# --- Load env file ---------------------------------------------------------
ENV_FILE=".env.${platform}.${tenant}"
print_section "Loading environment file: $ENV_FILE"
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
    print_success "Environment variables loaded"
else
    print_error "Environment file not found: $ENV_FILE"
    exit 1
fi

# --- Run Python scripts ----------------------------------------------------
print_section "Running Keycloak configuration"
python keycloak/keycloak_config.py && print_success "Keycloak config completed"

print_section "Running Vault configuration"
python main.py tenant enable --name cosmotech --engine v1 && print_success "Tenant enabled"
python main.py config write --resource all --use-azure --engine v1 --platform-id $tenant && print_success "Vault config written"