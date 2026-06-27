# Newclid Backend - NOTICE

The Newclid backend service was developed in 2026 as part of the
TU Delft Computer Science and Engineering Software Project, where the project
team worked on extending Newclid with a web backend for submitting and running
Newclid/Yuclid solving jobs.

## Backend component authors and contributors

Copyright 2026 Simeon Vutov

The initial Newclid backend module was created by Simeon Vutov. It includes the
FastAPI service structure, job submission API, Redis/RQ integration, backend
schemas, runner integration, Newclid execution adapter, and backend test setup.

## Third-party software notices

The backend component uses third-party Python packages for the API server,
request validation, background job processing, Redis communication, testing, and
build tooling.

The currently declared direct backend dependencies include, at a high level:

* FastAPI, used to define the HTTP API and expose interactive API
  documentation;
* redis-py, used as the Python client for connecting to the Redis-compatible
  queue backend;
* RQ, used to enqueue and process long-running Newclid solver jobs in worker
  processes;
* Uvicorn, used as the ASGI server for running the FastAPI application;
* pytest, used for backend unit and integration tests;
* HTTPX, used by the FastAPI/TestClient testing stack;
* uv_build, used as the backend Python build backend.

A generated list of direct and transitive Python package licenses is provided
in:

[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)

That file is generated from the installed backend Python environment and should
be regenerated whenever `pyproject.toml` or the backend lockfile changes.

## Redis-compatible server notice

The backend is designed to use a Redis-compatible server for queue storage and
temporary job state. The Python package `redis` listed in the generated license
report is only the Redis Python client.

If a Redis-compatible server binary or Docker image is distributed together with
the backend, its license must be checked separately for the exact server version
or image being distributed. This backend notice covers the Python backend
package dependencies, not the Redis server itself.

