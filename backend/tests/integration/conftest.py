from collections.abc import Callable

import pytest
from newclid_backend.queue import newclid_queue, redis_connection
from rq import SimpleWorker


@pytest.fixture(autouse=True)
def isolate_redis() -> None:
    redis_connection.flushdb()
    yield
    redis_connection.flushdb()


@pytest.fixture
def run_burst_worker() -> Callable[[], None]:
    def _run() -> None:
        worker = SimpleWorker([newclid_queue], connection=redis_connection)
        worker.work(burst=True)

    return _run
