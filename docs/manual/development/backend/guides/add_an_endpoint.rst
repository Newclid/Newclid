Backend guide to adding an endpoint
===================================

Use this guide when adding a new HTTP endpoint to the backend service.

Backend endpoint checklist
--------------------------

1. Decide whether the endpoint belongs in an existing router.

   Job-related endpoints should usually stay in ``routers/jobs.py``. If the new
   endpoint introduces a new resource, create a new router under
   ``src/newclid_backend/routers/``.

2. Define request and response models in ``schemas.py``.

   Use Pydantic models for public input and output. Avoid returning raw internal
   objects from Newclid, RQ, or Redis.

3. Implement the route.

   Keep route handlers small. They should validate input, call service/helper
   functions, and translate expected failures into ``HTTPException``.

4. Register the router in ``main.py``.

   Existing job routes are registered with ``app.include_router``.

5. Update documentation.

   Add the endpoint to :doc:`../modules/api` and, if it is part of a
   frontend/backend boundary, add or update a page under
   :doc:`../../contracts/index`.

6. Add tests.

   Add unit tests for validation and route behavior. Add integration tests when
   the endpoint depends on Redis, RQ, or Newclid execution.

Backend endpoint example pattern
--------------------------------

.. code-block:: python

   from fastapi import APIRouter
   from pydantic import BaseModel

   router = APIRouter(prefix="/api/example", tags=["example"])

   class ExampleResponse(BaseModel):
       status: str

   @router.get("", response_model=ExampleResponse)
   def read_example() -> ExampleResponse:
       return ExampleResponse(status="ok")

Backend endpoint review questions
---------------------------------

Before opening the merge request, check:

- Does the endpoint expose a stable public model?
- Does the endpoint avoid long-running work inside the request handler?
- Are expected errors converted to useful HTTP status codes?
- Does the endpoint need frontend documentation or a shared contract page?
- Are unit and integration tests placed in the right test layer?
