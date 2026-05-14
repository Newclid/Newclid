from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi import status as http_status

from newclid_backend.queue import enqueue_job
from newclid_backend.schemas import (
    CreateJobRequest,
    CreateJobResponse,
    JobResultResponse,
    JobStatusResponse,
)
from newclid_backend.tasks import run_newclid_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=CreateJobResponse)
def create_job(request: CreateJobRequest) -> CreateJobResponse:
    job_id = str(uuid4())
    jgex_problem = request.problem_input.strip()

    try:
        enqueue_job(
            run_newclid_job,
            jgex_problem,
            request.timeout_seconds,
            job_id=job_id,
            timeout_seconds=request.timeout_seconds,
        )
    except Exception as error:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not enqueue a new Newclid job: {error}",
        )

    return CreateJobResponse(job_id=job_id, status="queued")


@router.get("/{job_id}", response_model=JobStatusResponse)
def check_job_status(job_id: str) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job_id, status="queued", message="Job status endpoint is available"
    )


@router.get("/{job_id}/result", response_model=JobResultResponse)
def check_job_result(job_id: str) -> JobResultResponse:
    return JobResultResponse(job_id=job_id, status="queued", result=None, error=None)
