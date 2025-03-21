from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass
class Config:
    host: str
    environment_id: int
    token: str
    project_dir: str | None
    dbt_core_enabled: bool
    semantic_layer_enabled: bool
    discovery_enabled: bool
    dbt_command: str

def _validate_env_vars(
    *, host: str | None, environment_id: str | None, token: str | None, project_dir: str | None
) -> tuple[str, str, str, str | None]:
    if not host or not environment_id or not token:
        raise ValueError(
            "Missing at least one of these required environment variables: " +
            "DBT_HOST, DBT_ENV_ID, DBT_TOKEN."
        )
    if host.startswith("metadata") or host.startswith("semantic-layer"):
        raise ValueError("Host must not start with 'metadata' or 'semantic-layer'.")
    if not project_dir and not os.getenv("DISABLE_DBT_CORE"):
        raise ValueError("Project directory is required when dbt core MCP is enabled.")
    return host, environment_id, token, project_dir

def load_config() -> Config:
    load_dotenv()

    host = os.environ.get("DBT_HOST")
    environment_id = os.environ.get("DBT_ENV_ID")
    token = os.environ.get("DBT_TOKEN")
    project_dir = os.environ.get("DBT_PROJECT_DIR")

    host, environment_id, token, project_dir = _validate_env_vars(host=host, environment_id=environment_id, token=token, project_dir=project_dir)

    return Config(
        host=host,
        environment_id=int(environment_id),
        token=token,
        project_dir=project_dir,
        dbt_core_enabled=os.getenv("DISABLE_DBT_CORE") != "true",
        semantic_layer_enabled=os.getenv("DISABLE_SEMANTIC_LAYER") != "true",
        discovery_enabled=os.getenv("DISABLE_DISCOVERY") != "true",
        dbt_command=os.getenv("DBT_PATH", "dbt"),
    )
