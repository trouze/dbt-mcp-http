from dataclasses import dataclass
from enum import Enum


class GroupByType(Enum):
    CATEGORICAL_DIMENSION = "categorical_dimension"
    TIME_DIMENSION = "time_dimension"
    ENTITY = "entity"


@dataclass(frozen=True)
class GroupByParam:
    """Parameter for a group_by, i.e a dimension or an entity."""

    name: str
    type: GroupByType
    grain: str | None
