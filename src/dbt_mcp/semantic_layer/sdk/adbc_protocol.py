import json
from typing import Any

from dbtsl.api.adbc.protocol import ADBCProtocol as OfficialADBCProtocol
from dbtsl.api.shared.query_params import (
    OrderByGroupBy,
    OrderByMetric,
)

from dbt_mcp.semantic_layer.sdk.query_params import GroupByParam, GroupByType


class ADBCProtocol(OfficialADBCProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def _serialize_val(cls, val: Any) -> str:
        if isinstance(val, bool):
            return str(val)

        if isinstance(val, list):
            list_str = ",".join(cls._serialize_val(list_val) for list_val in val)  # pyright: ignore[reportUnknownVariableType]
            return f"[{list_str}]"

        if isinstance(val, OrderByMetric):
            m = f'Metric("{val.name}")'
            if val.descending:
                m += ".descending(True)"
            return m

        if isinstance(val, OrderByGroupBy):
            d = f'Dimension("{val.name}")'
            if val.grain:
                grain_str = val.grain.lower()
                d += f'.grain("{grain_str}")'
            if val.descending:
                d += ".descending(True)"
            return d

        if isinstance(val, GroupByParam):
            g: str = ""
            if val.type == GroupByType.CATEGORICAL_DIMENSION:
                g = f'Dimension("{val.name}")'
            elif val.type == GroupByType.ENTITY:
                g = f'Entity("{val.name}")'
            else:  # val.type == GroupByType.TIME_DIMENSION
                g = f'TimeDimension("{val.name}", "{val.grain}")'
            return g

        return json.dumps(val)
