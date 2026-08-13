import os
import uuid

import pytest
from fastapi.testclient import TestClient

# Variables antes de importar app/database: el engine se crea en import-time
os.environ.setdefault("SECRET_KEY", "test-secret-key-pytest-only-32chars-min")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pokemon_pytest.db")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.pop("DOCKER_CONTAINER", None)
os.environ.pop("PORT", None)

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:12]}@example.com"
