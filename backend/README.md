# Newclid Backend

This package contains the FastAPI backend for the Newclid web application.

The backend is responsible for receiving problem input from the frontend, creating background solver jobs, and exposing endpoints for checking job status and retrieving results. Long-running solver work should not be executed directly inside FastAPI request handlers. Instead, jobs are queued through RQ and processed by separate worker processes.

## Current backend responsibilities

At this stage, the backend provides:

- A FastAPI application
- Job-related API schemas
- Placeholder job endpoints
- Redis/RQ queue configuration

The Newclid subprocess runner is implemented separately in a later task.

## Requirements

You need:

- Python environment managed through `uv`
- A Redis-compatible server
- Backend Python dependencies installed through `uv`

The backend uses RQ for background jobs. RQ stores queued jobs, job metadata, and short-lived results in a Redis-compatible server.

Redis and Valkey are both acceptable Redis-compatible servers.

## Redis-compatible server setup

The backend expects a Redis-compatible server to be reachable at:

```text
redis://localhost:6379/0
```

This is the default configuration. You can either install Redis/Valkey locally or run it through Docker.

### Option 1: Use Docker

This is the easiest cross-platform option.

From any directory, run:

```bash
docker run --rm -p 6379:6379 redis:7
```

This starts a Redis server on your machine at port `6379`.

### Option 2: Install Redis or Valkey locally

Install either Redis or Valkey using your operating system's package manager.

The backend does not depend on the exact implementation, as long as it provides a Redis-compatible server on port `6379`.

After starting the server, verify that it responds with:

```bash
redis-cli ping
```

or, if using Valkey:

```bash
valkey-cli ping
```

Expected output:

```text
PONG
```

## Configuration

The backend reads queue configuration from environment variables.

Default values:

```text
REDIS_URL=redis://localhost:6379/0
NEWCLID_QUEUE_NAME=newclid
DEFAULT_JOB_TIMEOUT_SECONDS=120
RESULT_TTL_SECONDS=3600
FAILURE_TTL_SECONDS=3600
```

Meaning:

- `REDIS_URL`: connection URL for the Redis-compatible server
- `NEWCLID_QUEUE_NAME`: name of the RQ queue used for solver jobs
- `DEFAULT_JOB_TIMEOUT_SECONDS`: default maximum runtime for a background job
- `RESULT_TTL_SECONDS`: how long successful job results are kept
- `FAILURE_TTL_SECONDS`: how long failed job information is kept

### Optional local `.env` file

The backend has safe defaults, so a `.env` file is not required for the standard local setup.

If you want to override configuration locally, create:

```text
backend/.env
```

Example:

```env
REDIS_URL=redis://localhost:6379/0
NEWCLID_QUEUE_NAME=newclid
DEFAULT_JOB_TIMEOUT_SECONDS=120
RESULT_TTL_SECONDS=3600
FAILURE_TTL_SECONDS=3600
```

## Installing backend dependencies

From the `backend/` directory:

```bash
uv sync
```

## Running the backend

From the `backend/` directory:

```bash
uv run uvicorn newclid_backend.main:app --reload
```

The backend runs by default at:

```text
http://127.0.0.1:8000
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

FastAPI API docs are available at:

```text
http://127.0.0.1:8000/docs
```
