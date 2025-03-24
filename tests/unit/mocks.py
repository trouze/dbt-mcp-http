from dbtsl.models.dimension import Dimension
from dbtsl.models.metric import Metric
from contextlib import contextmanager

class MockSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class MockSemanticLayerClient:
    def __init__(self, metrics: list[Metric] = [], dimensions: list[Dimension] = []):
        self.mocked_metrics = metrics
        self.mocked_dimensions = dimensions

    def metrics(self):
        return self.mocked_metrics

    def dimensions(self, metrics: list[str]):
        return self.mocked_dimensions

    @contextmanager
    def session(self):
        yield MockSession()
