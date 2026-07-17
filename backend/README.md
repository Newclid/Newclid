# Newclid Backend

FastAPI backend for the Newclid web application.

The backend receives geometry problems from the frontend, creates background
solver jobs, runs Newclid/Yuclid through worker processes, and exposes API
endpoints for checking job status and retrieving proof results.

Long-running solver work is not executed inside FastAPI request handlers.
Instead, submitted jobs are queued with RQ and processed by a separate worker
process using Redis as the queue backend.

## Overview

The backend provides:

* FastAPI application setup;
* health check endpoint;
* job creation, status, and result endpoints;
* request and response schemas;
* custom theorem payload validation;
* Redis/RQ queue integration;
* background worker task adapter;
* Newclid runner integration for JGEX problems;
* proof text, proof sections, run info, and sketch-point result formatting;
* unit and integration tests.

The basic flow is:

```text
frontend
  -> POST /api/jobs
  -> FastAPI backend enqueues job
  -> Redis/RQ stores job
  -> worker runs Newclid/Yuclid
  -> result is stored in Redis
  -> frontend polls status/result endpoints
```

## Runtime model

The backend has two runtime processes:

1. **API server**: receives HTTP requests, validates input, enqueues jobs, and
   exposes job status/result endpoints.
2. **Worker**: consumes jobs from the queue and runs the Newclid/Yuclid solving
   logic.

Both processes must use the same Redis instance and queue name. If the API is
running but the worker is not running, submitted jobs will remain queued.

## Requirements

You need:

* Python 3.11+;
* `uv`;
* a Redis-compatible server;
* Newclid available in the Python environment for real solver jobs.

Install backend dependencies from `backend/`:

```bash
uv sync
```

Install backend test dependencies:

```bash
uv sync --extra test
```

## Configuration

The backend reads configuration from environment variables.

Default values:

```text
REDIS_URL=redis://localhost:6379/0
NEWCLID_QUEUE_NAME=newclid
DEFAULT_JOB_TIMEOUT_SECONDS=120
RESULT_TTL_SECONDS=3600
FAILURE_TTL_SECONDS=3600
NEWCLID_COMMAND=newclid
MAX_OUTPUT_CHARS=200000
```

Meaning:

* `REDIS_URL`: Redis-compatible server used by RQ;
* `NEWCLID_QUEUE_NAME`: queue name used by both the API and worker;
* `DEFAULT_JOB_TIMEOUT_SECONDS`: default maximum runtime for a solver job;
* `RESULT_TTL_SECONDS`: how long successful job results remain available;
* `FAILURE_TTL_SECONDS`: how long failed job information remains available;
* `NEWCLID_COMMAND`: command name for Newclid-related execution paths;
* `MAX_OUTPUT_CHARS`: maximum stored stdout/stderr/proof output length.

A local `.env` file is optional. The default setup works for local development
with Redis running on `localhost:6379`.

## Running locally without Docker Compose

For local backend development, run Redis, the API server, and the worker in
separate terminals.

### 1. Start Redis

```bash
docker run --rm -p 6379:6379 redis:7
```

Check Redis:

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

### 2. Start the API server

From `backend/`:

```bash
uv run uvicorn newclid_backend.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Start the worker

From `backend/` in another terminal:

```bash
uv run rq worker newclid
```

On Windows, use the simple worker:

```bash
uv run rq worker --worker-class rq.worker.SimpleWorker newclid
```

The queue name must match `NEWCLID_QUEUE_NAME`. By default, this is `newclid`.

## Running with Docker Compose

In Docker Compose, the backend is represented by two services:

* `api`: runs the FastAPI/Uvicorn server;
* `worker`: runs the RQ worker.

Redis runs as a separate service and is shared by both backend services.

### Backend services only

From the repository root:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up --build api worker redis
```

This starts the backend API, backend worker, and Redis.

Depending on the Compose override, the API container may only be reachable inside
the Docker network. In the normal full-stack setup, the frontend web container
proxies `/api/` requests to the backend.

### Full local stack

From the repository root:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up --build
```

This starts:

* `web`: frontend nginx container;
* `api`: backend API container;
* `worker`: backend worker container;
* `redis`: Redis queue/storage service.

The frontend is exposed at:

```text
http://127.0.0.1:8080
```

Backend health check through the full stack:

```bash
curl http://127.0.0.1:8080/api/health
```

Stop the stack:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  down
```

## API endpoints

### Health check

```text
GET /api/health
```

Returns:

```json
{"status":"ok"}
```

### Create job

```text
POST /api/jobs
```

Creates a solver job and returns a `job_id`.

The request accepts:

* `input_type`: currently `jgex`;
* `problem_input`: JGEX problem text;
* `custom_theorems`: optional custom theorem definitions;
* `timeout_seconds`: optional job timeout.

### Check job status

```text
GET /api/jobs/{job_id}
```

Possible public statuses:

```text
queued
running
succeeded
failed
timed_out
cancelled
```

### Fetch job result

```text
GET /api/jobs/{job_id}/result
```

For successful jobs, the result can include:

* human-readable proof text;
* structured proof sections;
* solver run information;
* sketch points for frontend proof drawing;
* stdout/stderr fields.

## Testing

The backend uses `pytest`. Tests are split by how much of the system they
exercise.

```text
backend/tests/
├── unit/          isolated backend tests
└── integration/   Redis/RQ and Newclid runner integration tests
```

### Unit tests

Unit tests check individual backend modules in isolation. They do not require a
real Redis server, a running worker, or a real Newclid/Yuclid solver run.

They cover behavior such as:

* health endpoint behavior;
* request and response schema validation;
* job input normalization;
* custom theorem validation;
* job status and message mapping;
* queue helper behavior with mocked dependencies;
* runner helper functions.

From the repository root:

```bash
uv venv
uv pip install -e "backend[test]"
.venv/bin/python -m pytest backend/tests/unit
```

Or from `backend/`:

```bash
uv sync --extra test
uv run --extra test pytest tests/unit
```

### Integration tests

Integration tests check multiple backend components working together. Some of
them require external services or the full Newclid/Yuclid environment.

#### Redis/RQ integration tests

Redis/RQ integration tests require a real Redis-compatible server. They exercise
job creation, queue storage, worker execution, job status handling, and result
retrieval.

Start Redis:

```bash
docker run --rm -p 6379:6379 redis:7
```

Then run the Redis/RQ integration tests from the repository root:

```bash
uv venv
uv pip install -e "backend[test]"

REDIS_URL=redis://127.0.0.1:6379/15 \
  .venv/bin/python -m pytest backend/tests/integration -m redis
```

The `/15` Redis database keeps test data separate from the default local Redis
database.

#### Newclid runner integration tests

The Newclid runner integration tests execute the backend runner against real
JGEX input. These tests require the full Newclid/Yuclid environment to be
available, so they are slower than normal backend tests.

From the repository root:

```bash
uv sync
uv run pytest backend/tests/integration -m slow
```

This may build or prepare parts of the full Newclid/Yuclid environment.

### Common test commands

Run all backend unit tests:

```bash
.venv/bin/python -m pytest backend/tests/unit
```

Run all backend integration tests, with Redis running and the full environment
available:

```bash
REDIS_URL=redis://127.0.0.1:6379/15 \
  uv run pytest backend/tests/integration
```

Run tests that do not require Redis:

```bash
uv run pytest backend/tests -m "not redis"
```

Run tests that skip the slow real-runner path:

```bash
uv run pytest backend/tests -m "not slow"
```

Run only fast backend tests:

```bash
uv run pytest backend/tests -m "not redis and not slow"
```

### Coverage

Coverage can be run with `pytest-cov` as a temporary `uv` dependency.

Unit-test coverage:

```bash
uv run --with pytest-cov \
  pytest backend/tests/unit \
  --cov=newclid_backend \
  --cov-report=term-missing \
  --cov-report=html
```

Full backend coverage, with Redis running and the full environment available:

```bash
REDIS_URL=redis://127.0.0.1:6379/15 \
  uv run --with pytest-cov \
  pytest backend/tests \
  --cov=newclid_backend \
  --cov-report=term-missing \
  --cov-report=html
```

The HTML coverage report is written to:

```text
htmlcov/
```

## Project layout

```text
backend/
├── src/
│   └── newclid_backend/
│       ├── main.py              FastAPI app setup and health endpoint
│       ├── queue.py             Redis/RQ connection and job helpers
│       ├── tasks.py             RQ task adapter
│       ├── newclid_runner.py    Newclid/JGEX runner integration
│       ├── runner_helpers.py    runner helper functions
│       ├── runner_models.py     internal runner result models
│       ├── schemas.py           API request/response models
│       ├── settings.py          environment-based configuration
│       └── routers/
│           └── jobs.py          job create/status/result endpoints
├── tests/
│   ├── unit/                    isolated backend unit tests
│   └── integration/             Redis/RQ and runner integration tests
├── pyproject.toml
├── README.md
├── NOTICE.md
└── THIRD_PARTY_LICENSES.md
```

## Development notes

Keep API and worker responsibilities separate:

* FastAPI handlers should validate input, enqueue jobs, and return status/result
  data.
* Workers should execute solver jobs and return serializable result objects.
* Long-running Newclid/Yuclid work should not happen inside request handlers.
* Redis is used for temporary job state, not permanent user storage.

## Third-party licenses

Backend third-party Python license information is listed in:

```text
THIRD_PARTY_LICENSES.md
```

Regenerate it after dependency changes:

```bash
uv run --extra test \
  --with pip-licenses \
  --with uv_build \
  pip-licenses \
  --format=markdown \
  --with-urls \
  --ignore-packages newclid-backend pip-licenses prettytable wcwidth \
  --output-file THIRD_PARTY_LICENSES.generated.md
```

Then prepend the backend license report header before replacing
`THIRD_PARTY_LICENSES.md`.

