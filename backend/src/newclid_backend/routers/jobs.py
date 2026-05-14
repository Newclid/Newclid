from uuid import uuid4

from fastapi import APIRouter

from ..schemas import (
    CreateJobRequest,
    CreateJobResponse,
    JobResultResponse,
    JobStatusResponse,
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=CreateJobResponse)
def create_job(request: CreateJobRequest) -> CreateJobResponse:
    print(request.problem_input)

    return CreateJobResponse(job_id=str(uuid4()), status="queued")


@router.get("/{job_id}", response_model=JobStatusResponse)
def check_job_status(job_id: str) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job_id, status="queued", message="Job status endpoint is available"
    )


@router.get("/{job_id}/result", response_model=JobResultResponse)
def check_job_result(job_id: str) -> JobResultResponse:
    return JobResultResponse(job_id=job_id, status="queued", result=None, error=None)
