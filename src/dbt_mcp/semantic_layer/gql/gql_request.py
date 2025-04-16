from dataclasses import dataclass

import requests

from dbt_mcp.gql.errors import raise_gql_error


@dataclass
class ConnAttr:
    host: str
    params: dict
    auth_header: str


def submit_request(
    conn_attr: ConnAttr,
    payload: dict,
) -> dict:
    url = f"{conn_attr.host}/api/graphql"
    if "variables" not in payload:
        payload["variables"] = {}
    payload["variables"]["environmentId"] = conn_attr.params["environmentid"]
    r = requests.post(
        url,
        json=payload,
        headers={
            "Authorization": conn_attr.auth_header,
            "x-dbt-partner-source": "dbt-mcp",
        },
    )
    result = r.json()
    raise_gql_error(result)
    return result
