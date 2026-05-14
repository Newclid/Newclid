from typing import Any

from redis import Redis
from rq import Queue
from rq.job import Job, NoSuchJobError

from newclid_backend.settings import (
    DEFAULT_JOB_TIMEOUT_SECONDS,
    FAILURE_TTL_SECONDS,
    NEWCLID_QUEUE_NAME,
    REDIS_URL,
    RESULT_TTL_SECONDS,
)

redis_connection = Redis.from_url(REDIS_URL)
newclid_queue = Queue(NEWCLID_QUEUE_NAME, connection=redis_connection)


def enqueue_job(
    func: Any,
    *args: Any,
    job_id: str | None = None,
    timeout_seconds: int = DEFAULT_JOB_TIMEOUT_SECONDS,
    **kwargs: Any,
) -> Job:
    return newclid_queue.enqueue(
        func,
        *args,
        **kwargs,
        job_id=job_id,
        job_timeout=timeout_seconds,
        result_ttl=RESULT_TTL_SECONDS,
        failure_ttl=FAILURE_TTL_SECONDS,
    )


def fetch_job(job_id: str) -> Job | None:
    try:
        return Job.fetch(job_id, connection=redis_connection)
    except NoSuchJobError:
        return None


def map_rq_status(status: str) -> str:
    match status:
        case "queued" | "deferred" | "scheduled":
            return "queued"
        case "started":
            return "running"
        case "finished":
            return "succeeded"
        case "failed":
            return "failed"
        case "stopped" | "canceled":
            return "canceled"
        case _:
            return "failed"


def get_job_status(job_id: str) -> str | None:
    job = fetch_job(job_id)

    if job is None:
        return None

    return map_rq_status(job.get_status())
