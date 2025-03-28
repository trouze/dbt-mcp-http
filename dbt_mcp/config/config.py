from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass
class Config:
    host: str | None
    environment_id: int | None
    token: str | None
    project_dir: str | None
    dbt_cli_enabled: bool
    semantic_layer_enabled: bool
    discovery_enabled: bool
    remote_enabled: bool
    dbt_command: str
    dbt_executable_type: str
    remote_mcp_url: str
    multicell_account_prefix: str | None

def load_config() -> Config:
    load_dotenv()

    host = os.environ.get("DBT_HOST")
    environment_id = os.environ.get("DBT_ENV_ID")
    token = os.environ.get("DBT_TOKEN")
    project_dir = os.environ.get("DBT_PROJECT_DIR")
    dbt_path = os.environ.get("DBT_PATH", "dbt")
    dbt_executable_type = os.environ.get("DBT_EXECUTABLE_TYPE", "cloud")
    disable_dbt_cli = os.environ.get("DISABLE_DBT_CLI", "false") == "true"
    disable_semantic_layer = os.environ.get("DISABLE_SEMANTIC_LAYER", "false") == "true"
    disable_discovery = os.environ.get("DISABLE_DISCOVERY", "false") == "true"
    disable_remote = os.environ.get("DISABLE_REMOTE", "false") == "true"
    remote_mcp_url = os.environ.get("REMOTE_MCP_URL", "http://localhost:8000/mcp/sse")
    multicell_account_prefix = os.environ.get("MULTICELL_ACCOUNT_PREFIX", None)

    errors = []
    if not disable_semantic_layer or not disable_discovery:
        if not host:
            errors.append("DBT_HOST environment variable is required when semantic layer or discovery is enabled.")
        if not environment_id:
            errors.append("DBT_ENV_ID environment variable is required when semantic layer or discovery is enabled.")
        if not token:
            errors.append("DBT_TOKEN environment variable is required when semantic layer or discovery is enabled.")
        if host and (host.startswith("metadata") or host.startswith("semantic-layer")):
            errors.append("DBT_HOST must not start with 'metadata' or 'semantic-layer'.")
    if not disable_dbt_cli:
        if not project_dir:
            errors.append("DBT_PROJECT_DIR environment variable is required when dbt CLI MCP is enabled.")
        if not dbt_path:
            errors.append("DBT_PATH environment variable is required when dbt CLI MCP is enabled.")
        if dbt_executable_type not in ["core", "cloud"]:
            errors.append("DBT_EXECUTABLE_TYPE environment variable must be either 'core' or 'cloud' when dbt CLI MCP is enabled.")

    if errors:
        raise ValueError("Errors found in configuration:\n\n" + "\n".join(errors))

    return Config(
        host=host,
        environment_id=int(environment_id) if environment_id else None,
        token=token,
        project_dir=project_dir,
        dbt_cli_enabled=not disable_dbt_cli,
        semantic_layer_enabled=not disable_semantic_layer,
        discovery_enabled=not disable_discovery,
        remote_enabled=not disable_remote,
        dbt_command=dbt_path,
        dbt_executable_type=dbt_executable_type,
        remote_mcp_url=remote_mcp_url,
        multicell_account_prefix=multicell_account_prefix,
    )
