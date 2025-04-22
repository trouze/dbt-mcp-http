#!/bin/bash

# This script installs and manages the dbt-mcp server installation.
# It handles fresh installations, updates, and removals of the dbt-mcp package
# in a virtual environment under the user's home directory.
#
# Copyright 2025 dbt Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script is designed to be run on macOS.

mcp_server_dir="${HOME}/.dbt-mcp"

function check_existing_installation() {
    if [[ -d "${mcp_server_dir}" && -f "${mcp_server_dir}/.venv/bin/dbt-mcp" ]]; then
        echo "dbt-mcp is already installed in ${mcp_server_dir}."
        echo "How would you like to proceed?"
        echo "1. Remove the existing installation and start fresh"
        echo "2. Try to update the existing installation"
        echo "3. Abort! Abort!"

        read -p "Enter your choice (1-3): " choice

        case "${choice}" in
        1)
            echo "Removing existing installation..."
            rm -rf "${mcp_server_dir}"
            echo "Existing installation removed. Continuing with fresh install..."
            ;;
        2)
            update_existing_installation
            exit 0
            ;;
        3)
            echo "Installation aborted. Bye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please enter 1, 2, or 3."
            exit 1
            ;;
        esac
    fi
}

function update_existing_installation() {
    echo "Attempting to update existing installation..."
    cd "${mcp_server_dir}" || exit 1
    if [[ -f ".venv/bin/activate" ]]; then
        . .venv/bin/activate
        pip install --upgrade dbt-mcp
        echo "Update completed."
        echo "We hope you'll like the new version!"
    else
        echo "Error: Failed to activate virtual environment."
        echo "Please choose option 1 to start fresh."
        exit 1
    fi
}

function python() {
    # check if it's python or python3
    if command -v python3 &>/dev/null; then
        echo "python3"
    else
        echo "python"
    fi
}

function check_python() {
    # check if python is installed
    if ! command -v $(python) &>/dev/null; then
        echo "Python is not installed. Please install Python and try again."
        exit 1
    fi

    # check if python version is 3.12 or higher
    python_version=$($(python) --version 2>&1 | awk '{print $2}')
    major_version=$(echo "${python_version}" | cut -d. -f1)
    minor_version=$(echo "${python_version}" | cut -d. -f2)

    if [[ "${major_version}" -lt 3 ]] || ([[ "${major_version}" -eq 3 ]] && [[ "${minor_version}" -lt 12 ]]); then
        echo "Python version ${python_version} is not supported. Please install Python 3.12 or higher."
        exit 1
    fi
}

# Function to prompt for input with a default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"

    if [[ -z "${default}" ]]; then
        default_text=""
    else
        default_text=" [${default}]"
    fi

    read -p "${prompt}${default_text}: " input

    if [[ -z "${input}" ]]; then
        input="${default}"
    fi
    echo "${input}"
}

function install_dbt_mcp_package() {
    local target_package="$1"
    # sanity check to make sure the target package is dbt-mcp
    if [[ -n "${target_package}" && ! "${target_package}" =~ "dbt-mcp" ]]; then
        echo "========================================================="
        echo "Hold on! This does not look like a valid dbt-mcp package."
        echo "========================================================="
        read -p "Are you sure you want to install ${target_package}? (y/n): " confirm
        if [[ ! "${confirm}" =~ ^[Yy]$ ]]; then
            echo "Installation aborted. Bye!"
            exit 0
        fi
    fi

    if [[ -z "${target_package}" ]]; then
        target_package="dbt-mcp"
    fi

    current_dir=$(pwd)
    mkdir -p "${mcp_server_dir}"
    cd "${mcp_server_dir}" || exit 1
    $(python) -m venv .venv
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
        if ! pip install "${target_package}"; then
            echo "Error: Failed to install ${target_package}"
            exit 1
        fi
        deactivate
        ln -s "${mcp_server_dir}/.venv/bin/dbt-mcp" dbt-mcp
        cd "${current_dir}" || exit 1
        echo "dbt-mcp installed in ${mcp_server_dir}"
    else
        echo "Error: Failed to activate virtual environment."
        exit 1
    fi
}

function configure_environment() {
    # Create .env file
    echo ""
    echo "-----------------------------------------------------------------------"
    echo "We need a couple of details about your dbt project to get started."
    echo "You can always adjust the configuration later in ${mcp_server_dir}/.env"
    echo "-----------------------------------------------------------------------"
    echo ""
    touch "${mcp_server_dir}/.env"

    # Prompt for environment variables with defaults
    echo "Your dbt Cloud instance hostname."
    echo "This will look like an \`Access URL\` found at https://docs.getdbt.com/docs/cloud/about-cloud/access-regions-ip-addresses. If you are using Multi-cell, do not include the \`ACCOUNT_PREFIX\` here."
    DBT_HOST=$(prompt_with_default "Enter DBT_HOST" "cloud.dbt.com")

    echo "Your personal access token or service token. Service token is required when using the Semantic Layer."
    DBT_TOKEN=$(prompt_with_default "Enter DBT_TOKEN" "")

    echo "Your dbt Cloud user ID."
    DBT_USER_ID=$(prompt_with_default "Enter DBT_USER_ID")

    echo "The path to your dbt project directory."
    DBT_PROJECT_DIR=$(prompt_with_default "Enter DBT_PROJECT_DIR")

    echo "Your dbt Cloud production environment ID."
    DBT_PROD_ENV_ID=$(prompt_with_default "Enter DBT_PROD_ENV_ID")

    echo "Your dbt Cloud development environment ID."
    DBT_DEV_ENV_ID=$(prompt_with_default "Enter DBT_DEV_ENV_ID")

    echo "The path to your dbt Core or dbt Cloud CLI executable. You can find your dbt executable by running \`which dbt\`."
    DBT_PATH=$(prompt_with_default "Enter DBT_PATH")

    echo "If you are using Multi-cell, set this to your \`ACCOUNT_PREFIX\`. If you are not using Multi-cell, do not set this environment variable. You can learn more here : https://docs.getdbt.com/docs/cloud/about-cloud/access-regions-ip-addresses."
    MULTICELL_ACCOUNT_PREFIX=$(prompt_with_default "Enter MULTICELL_ACCOUNT_PREFIX" "")

    # Write to .env file
    cat >"${mcp_server_dir}/.env" <<EOF
DBT_HOST="${DBT_HOST}"
DBT_TOKEN="${DBT_TOKEN}"
DBT_PROD_ENV_ID="${DBT_PROD_ENV_ID}"
DBT_DEV_ENV_ID="${DBT_DEV_ENV_ID}"
DBT_USER_ID="${DBT_USER_ID}"
DBT_PROJECT_DIR="${DBT_PROJECT_DIR}"
DBT_PATH="${DBT_PATH}"
EOF

    if [[ -n "${MULTICELL_ACCOUNT_PREFIX}" ]]; then
        echo "MULTICELL_ACCOUNT_PREFIX=\"${MULTICELL_ACCOUNT_PREFIX}\"" >>"${mcp_server_dir}/.env"
    fi

    echo "Great! That's all we needed for now."
    echo "You can always adjust the configuration later in ${mcp_server_dir}/.env"
}

# make sure python is installed and has version 3.12 or higher
check_python

# check if mcp-dbt is already installed
check_existing_installation

# install dbt-mcp package
install_dbt_mcp_package "$1"

# configure environment
configure_environment

echo "Installation and configuration complete!"
echo "Have a great day!"
