from dataclasses import dataclass
from dbtsl.models.metric import MetricType
from dbtsl.models.dimension import DimensionType
from dbtsl.models.entity import EntityType


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


@dataclass
class EntityToolResponse:
    name: str
    type: EntityType
    description: str | None = None
