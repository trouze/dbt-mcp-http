from dbtsl.api.adbc.client.base import BaseADBCClient as OfficialBaseADBCClient

from dbt_mcp.semantic_layer.sdk.adbc_protocol import ADBCProtocol


class BaseADBCClient(OfficialBaseADBCClient):
    PROTOCOL = ADBCProtocol

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
