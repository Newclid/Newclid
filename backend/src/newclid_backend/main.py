from fastapi import FastAPI

from .routers.jobs import router as jobs_router

app = FastAPI(title="Newclid Backend")

app.include_router(jobs_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
