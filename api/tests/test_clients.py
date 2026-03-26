from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock

from falcon import HTTP_200, HTTP_201, HTTP_400, HTTP_409
from sqlalchemy.exc import IntegrityError


def _scope_factory(session):
    @contextmanager
    def _scope():
        yield session

    return _scope


def test_get_clients_empty_list(client, monkeypatch):
    mock_session = MagicMock()
    scalars_result = MagicMock()
    scalars_result.all.return_value = []
    mock_session.scalars.return_value = scalars_result
    monkeypatch.setattr("src.resources.clients.session_scope", _scope_factory(mock_session))

    result = client.simulate_get("/v1/clients")

    assert result.status == HTTP_200
    assert result.json == {"items": []}


def test_get_clients_returns_items(client, monkeypatch):
    rows = [
        SimpleNamespace(client_key="key-1", document_number="111", name="Alpha"),
        SimpleNamespace(client_key="key-2", document_number="222", name="Beta"),
    ]
    mock_session = MagicMock()
    scalars_result = MagicMock()
    scalars_result.all.return_value = rows
    mock_session.scalars.return_value = scalars_result
    monkeypatch.setattr("src.resources.clients.session_scope", _scope_factory(mock_session))

    result = client.simulate_get("/v1/clients")

    assert result.status == HTTP_200
    assert result.json == {
        "items": [
            {"client_key": "key-1", "document_number": "111", "name": "Alpha"},
            {"client_key": "key-2", "document_number": "222", "name": "Beta"},
        ]
    }


def test_post_clients_validation_error_missing_name(client, monkeypatch):
    mock_session = MagicMock()
    monkeypatch.setattr("src.resources.clients.session_scope", _scope_factory(mock_session))

    result = client.simulate_post(
        "/v1/clients",
        json={"document_number": "12345678901234"},
    )

    assert result.status == HTTP_400
    assert "name" in (result.json or {}).get("description", "").lower()


def test_post_clients_validation_error_document_number_too_long(client, monkeypatch):
    mock_session = MagicMock()
    monkeypatch.setattr("src.resources.clients.session_scope", _scope_factory(mock_session))

    result = client.simulate_post(
        "/v1/clients",
        json={"name": "Valid", "document_number": "x" * 19},
    )

    assert result.status == HTTP_400


def test_post_clients_invalid_body_not_object(client, monkeypatch):
    mock_session = MagicMock()
    monkeypatch.setattr("src.resources.clients.session_scope", _scope_factory(mock_session))

    result = client.simulate_post(
        "/v1/clients",
        body="[]",
        headers={"Content-Type": "application/json"},
    )

    assert result.status == HTTP_400


def test_post_clients_created(client, monkeypatch):
    mock_session = MagicMock()
    monkeypatch.setattr("src.resources.clients.session_scope", _scope_factory(mock_session))

    result = client.simulate_post(
        "/v1/clients",
        json={"name": "Acme Corp", "document_number": "12345678901234"},
    )

    assert result.status == HTTP_201
    assert result.json["name"] == "Acme Corp"
    assert result.json["document_number"] == "12345678901234"
    assert len(result.json["client_key"]) == 36
    assert result.headers.get("Location", "").endswith(result.json["client_key"])
