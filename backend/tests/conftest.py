import pytest
from fastapi.testclient import TestClient
from newclid_backend.main import app

VALID_JGEX_PROBLEM = (
    "a b c = triangle a b c; "
    "d = on_tline d b a c, on_tline d c a b; "
    "e = on_line e a c, on_line e b d "
    "? perp a d b c"
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def valid_jgex_problem() -> str:
    return VALID_JGEX_PROBLEM
