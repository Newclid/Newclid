from collections.abc import Callable, Iterator

import pytest
from newclid_backend.queue import newclid_queue, redis_connection
from rq import SimpleWorker


@pytest.fixture(autouse=True)
def isolate_redis(request: pytest.FixtureRequest) -> Iterator[None]:
    if "redis" not in request.keywords:
        yield
        return
    redis_connection.flushdb()
    yield
    redis_connection.flushdb()


@pytest.fixture
def run_burst_worker() -> Callable[[], None]:
    def _run() -> None:
        SimpleWorker([newclid_queue], connection=redis_connection).work(burst=True)

    return _run
