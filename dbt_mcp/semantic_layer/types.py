from dataclasses import dataclass
from dbtsl.models.metric import MetricType
from dbtsl.models.dimension import DimensionType

@dataclass
class MetricToolResponse:
    name: str
    type: MetricType
    label: str | None = None
    description: str | None = None

@dataclass
class DimensionToolResponse:
    name: str
    type: DimensionType
    description: str | None = None
    label: str | None = None
    granularities: list[str] | None = None
