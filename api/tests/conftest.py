import pytest
from falcon import testing


@pytest.fixture
def app():
    from main import create_app

    return create_app()


@pytest.fixture
def client(app):
    return testing.TestClient(app)
