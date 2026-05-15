from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
from rq.job import Job

from newclid_backend.queue import enqueue_job, fetch_job
from newclid_backend.schemas import (
    CreateJobRequest,
    CreateJobResponse,
    JobResultResponse,
    JobStatusResponse,
)
from newclid_backend.tasks import run_newclid_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# These are the public statuses which the job can be in
# Public means this is what we will expose as a status of a job
# Internally a job can be in these or in different statuses
PublicJobStatus = Literal[
    "queued",
    "running",
    "succeeded",
    "failed",
    "timed_out",
    "cancelled",
]


def _get_job_or_404(job_id: str) -> Job:
    job = fetch_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} was not found.",
        )

    return job


def _to_public_status(job: Job) -> PublicJobStatus:
    # Fetches the most recent status of a job
    # This is the status of a job according to
    # RQ (which is not the same as PublicJobStatus)
    rq_job_status = job.get_status(refresh=True)

    if rq_job_status in {"queued", "deferred", "scheduled"}:
        return "queued"
    if rq_job_status == "started":
        return "running"
    if rq_job_status in {"stopped", "canceled"}:
        return "cancelled"
    if rq_job_status == "failed":
        return "failed"
    if rq_job_status == "finished":
        result = job.return_value(refresh=True)

        if isinstance(result, dict):
            result_status = result.get("status")
            if result_status in {"succeeded", "failed", "timed_out"}:
                return result_status

    return "failed"


def _get_message_for_job(job: Job, public_status: PublicJobStatus) -> str:
    if public_status in {"succeeded", "failed", "timed_out"}:
        result = job.return_value(refresh=True)

        if isinstance(result, dict):
            message = result.get("message")

            if isinstance(message, str):
                return message

    match public_status:
        case "queued":
            return "Job is queued."
        case "running":
            return "Job is running."
        case "succeeded":
            return "Newclid completed successfully."
        case "failed":
            return "Newclid failed."
        case "timed_out":
            return "Newclid timed out."
        case "cancelled":
            return "Job was cancelled."


@router.post("", response_model=CreateJobResponse)
def create_job(request: CreateJobRequest) -> CreateJobResponse:
    job_id = str(uuid4())
    jgex_problem = request.problem_input.strip()

    try:
        enqueue_job(
            run_newclid_job,
            jgex_problem,
            job_id=job_id,
            timeout_seconds=request.timeout_seconds,
        )
    except Exception as error:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not enqueue a new Newclid job: {error}",
        ) from error

    return CreateJobResponse(job_id=job_id, status="queued")


@router.get("/{job_id}", response_model=JobStatusResponse)
def check_job_status(job_id: str) -> JobStatusResponse:
    job = _get_job_or_404(job_id)
    public_job_status = _to_public_status(job)

    return JobStatusResponse(
        job_id=job_id,
        status=public_job_status,
        message=_get_message_for_job(job, public_job_status),
    )


@router.get("/{job_id}/result", response_model=JobResultResponse)
def check_job_result(job_id: str) -> JobResultResponse:
    job = _get_job_or_404(job_id)
    public_job_status = _to_public_status(job)

    if public_job_status in {"queued", "running"}:
        return JobResultResponse(
            job_id=job_id, status=public_job_status, result=None, error=None
        )

    if public_job_status == "cancelled":
        return JobResultResponse(
            job_id=job_id,
            status=public_job_status,
            result=None,
            error="Job was cancelled.",
        )

    result = job.return_value(refresh=True)

    if isinstance(result, dict):
        error = None

        if public_job_status in {"failed", "timed_out"}:
            message = result.get("message")
            error = message if isinstance(message, str) else "Newclid job failed"

        return JobResultResponse(
            job_id=job_id, status=public_job_status, result=result, error=error
        )

    return JobResultResponse(
        job_id=job_id,
        status="failed",
        result=None,
        error="Newclid job failed for unknown reason",
    )
