from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass
class Config:
    host: str
    environment_id: int
    token: str

def _validate_env_vars(
    host: str | None, environment_id: str | None, token: str | None
) -> tuple[str, str, str]:
    if not host or not environment_id or not token:
        raise ValueError(
            "Missing at least one of these required environment variables: " +
            "DBT_HOST, DBT_ENV_ID, DBT_TOKEN."
        )
    if host.startswith("metadata") or host.startswith("semantic-layer"):
        raise ValueError("Host must not start with 'metadata' or 'semantic-layer'.")
    return host, environment_id, token

def load_config() -> Config:
    load_dotenv()

    host = os.environ.get("DBT_HOST")
    environment_id = os.environ.get("DBT_ENV_ID")
    token = os.environ.get("DBT_TOKEN")

    host, environment_id, token = _validate_env_vars(host, environment_id, token)

    return Config(
        host=host,
        environment_id=int(environment_id),
        token=token,
    )
