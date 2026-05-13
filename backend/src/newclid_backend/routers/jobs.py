from uuid import uuid4

from fastapi import APIRouter

from ..schemas import (
    CreateJobRequest,
    CreateJobResponse,
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=CreateJobResponse)
def create_job(request: CreateJobRequest) -> CreateJobResponse:
    print(request.problem_input)

    return CreateJobResponse(job_id=str(uuid4()), status="queued")
