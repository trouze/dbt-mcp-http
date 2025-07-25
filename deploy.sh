#!/bin/bash
set -e

echo "Deploying dbt-mcp-server to Azure Container Instances..."

# Source your secrets from a secure file (not in git)
if [ -f "secrets.env" ]; then
    source secrets.env
    echo "✅ Loaded configuration from secrets.env"
else
    echo "❌ Please create secrets.env with your values"
    echo "Copy docker.env to secrets.env and add Azure config:"
    echo "export RESOURCE_GROUP='dbtMCP'"
    echo "export REGISTRY_NAME='dbtmcpregistry'"
    echo "export CONTAINER_NAME='dbt-mcp-server'"
    echo "export LOCATION='centralus'"
    exit 1
fi

# Get ACR credentials
echo "🔐 Getting ACR credentials..."
ACR_LOGIN_SERVER=$(az acr show --name $REGISTRY_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query "passwords[0].value" --output tsv)

echo "🚀 Deploying container to ACI..."

# Delete existing container if it exists
if az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME &> /dev/null; then
    echo "🗑️  Deleting existing container..."
    az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes
fi

# Deploy with all environment variables from docker.env
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image $ACR_LOGIN_SERVER/dbt-mcp-server \
  --restart-policy Always \
  --registry-login-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label dbt-mcp-server-unique \
  --ports 80 \
  --os-type linux \
  --cpu 1 \
  --memory 2 \
  --environment-variables \
    PORT="80" \
    HOST="0.0.0.0" \
    DBT_HOST="$DBT_HOST" \
    DBT_PROD_ENV_ID="$DBT_PROD_ENV_ID" \
    DBT_DEV_ENV_ID="$DBT_DEV_ENV_ID" \
    DBT_USER_ID="$DBT_USER_ID" \
    DBT_PROJECT_DIR="$DBT_PROJECT_DIR" \
    DBT_PATH="$DBT_PATH" \
    DBT_REPO_URL="$DBT_REPO_URL" \
    DBT_REPO_BRANCH="$DBT_REPO_BRANCH" \
    MULTICELL_ACCOUNT_PREFIX="$MULTICELL_ACCOUNT_PREFIX" \
    ACCOUNT="$ACCOUNT" \
    USER="$USER" \
    KEY_PATH="$KEY_PATH" \
    ROLE="$ROLE" \
    WAREHOUSE="$WAREHOUSE" \
    DATABASE="$DATABASE" \
  --secure-environment-variables \
    DBT_TOKEN="$DBT_TOKEN" \
    GITHUB_TOKEN="$GITHUB_TOKEN" \
    PASSPHRASE="$PASSPHRASE"

echo ""
echo "🎉 Deployment complete!"
echo "📍 Container URL: http://dbt-mcp-server-unique.$LOCATION.azurecontainer.io:80"
echo "🏥 Health check: http://dbt-mcp-server-unique.$LOCATION.azurecontainer.io:80/health"
echo ""
echo "📊 Useful commands:"
echo "  Check status: az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query instanceView.state"
echo "  View logs: az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --follow"
echo "  Stream logs: az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --follow"
echo "  Delete container: az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes"