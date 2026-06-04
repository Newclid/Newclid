Newclid Backend - NOTICE
========================

The Newclid backend service was developed in 2026 as part of the
TU Delft Computer Science and Engineering Software Project, where the project
team worked on extending Newclid with a web backend for submitting and running
Newclid/Yuclid jobs.

Backend component authors and contributors
------------------------------------------

Copyright 2026 Simeon Vutov

The initial Newclid backend module was created by Simeon Vutov. It includes
the FastAPI service structure, job submission API, Redis/RQ integration,
backend schemas, runner integration, and backend test setup.

THIRD-PARTY SOFTWARE NOTICES
============================

The backend component directly depends on the following third-party software
components:

Runtime dependencies:

- FastAPI
- redis-py
- RQ
- Uvicorn

Development, testing, and build dependencies:

- pytest
- HTTPX
- uv_build

This notice lists the direct backend dependencies declared by the backend
package. Transitive dependency licenses should be reviewed from the lockfile or
from a generated dependency license report before a public binary or container
distribution.

--------------------------------------------------------------------------------

FastAPI
-------

FastAPI is licensed under the MIT License.

Copyright (c) 2018 Sebastián Ramírez

The full license text copied from the installed package is included under:

    third_party_licenses/fastapi/

--------------------------------------------------------------------------------

redis-py
--------

redis-py is licensed under the MIT License.

Copyright (c) 2022-2023, Redis, inc.

The full license text copied from the installed package is included under:

    third_party_licenses/redis-py/

--------------------------------------------------------------------------------

RQ
--

RQ (Redis Queue) is licensed under the BSD 2-Clause License.

Redis Queue is used by the backend for queueing and processing background jobs.

The full license text copied from the installed package is included under:

    third_party_licenses/rq/

--------------------------------------------------------------------------------

Uvicorn
-------

Uvicorn is licensed under the BSD 3-Clause License.

Copyright (c) 2017-present, Encode OSS Ltd.
All rights reserved.

The full license text copied from the installed package is included under:

    third_party_licenses/uvicorn/

--------------------------------------------------------------------------------

pytest
------

pytest is distributed under the terms of the MIT License.

Copyright Holger Krekel and others, 2004.

The full license text copied from the installed package is included under:

    third_party_licenses/pytest/

--------------------------------------------------------------------------------

HTTPX
-----

HTTPX is licensed under the BSD 3-Clause License.

Copyright (c) 2019-present, Encode OSS Ltd.
All rights reserved.

The full license text copied from the installed package is included under:

    third_party_licenses/httpx/

--------------------------------------------------------------------------------

uv_build
--------

uv_build is part of the uv project. The uv project is licensed under either
the Apache License, Version 2.0, or the MIT License, at the user's option.

Copyright (c) 2025 Astral Software Inc.

The full license text copied from the installed package is included under:

    third_party_licenses/uv-build/

--------------------------------------------------------------------------------

Redis server
------------

The backend is designed to use a Redis-compatible server for queue storage.
The Python package listed above as redis-py is only the Redis Python client.

If a Redis server binary or Docker image is distributed together with the
backend, its license must be checked separately for the exact Redis server
version being distributed. This notice covers the Python redis-py client only,
not the Redis server itself.
