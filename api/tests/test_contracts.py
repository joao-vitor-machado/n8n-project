from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock

from falcon import HTTP_200, HTTP_201, HTTP_400


def _scope_factory(session):
    @contextmanager
    def _scope():
        yield session

    return _scope


def test_get_contracts_empty_list(client, monkeypatch):
    client_row = SimpleNamespace(
        id=1,
        client_key="ckey",
        document_number="1",
        name="Acme",
    )
    m_client = MagicMock()
    m_client.first.return_value = client_row
    m_contracts = MagicMock()
    m_contracts.all.return_value = []
    mock_session = MagicMock()
    mock_session.scalars.side_effect = [m_client, m_contracts]
    monkeypatch.setattr("resources.contracts.session_scope", _scope_factory(mock_session))

    result = client.simulate_get("/v1/client/ckey/contract")

    assert result.status == HTTP_200
    assert result.json == {"items": []}


def test_post_contracts_unknown_client(client, monkeypatch):
    mock_session = MagicMock()
    scalars_result = MagicMock()
    scalars_result.first.return_value = None
    mock_session.scalars.return_value = scalars_result
    monkeypatch.setattr("resources.contracts.session_scope", _scope_factory(mock_session))

    result = client.simulate_post(
        "/v1/client/missing/contract",
        json={
            "start_date": "2024-06-01",
            "active": True,
        },
    )

    assert result.status == HTTP_400
    assert "client_key" in (result.json or {}).get("description", "").lower()


def test_post_contracts_created(client, monkeypatch):
    mock_session = MagicMock()
    client_row = SimpleNamespace(
        id=99,
        client_key="ckey",
        document_number="12345678901234",
        name="Acme",
    )
    scalars_result = MagicMock()
    scalars_result.first.return_value = client_row
    mock_session.scalars.return_value = scalars_result
    monkeypatch.setattr("resources.contracts.session_scope", _scope_factory(mock_session))

    result = client.simulate_post(
        "/v1/client/ckey/contract",
        json={
            "start_date": "2024-06-01",
            "active": False,
        },
    )

    assert result.status == HTTP_201
    assert result.json["active"] is False
    assert result.json["start_date"] == "2024-06-01"
    assert result.json["client"]["client_key"] == "ckey"
    assert len(result.json["contract_key"]) == 36
    loc = result.headers.get("Location", "")
    assert loc.endswith(result.json["contract_key"])
    assert "/v1/client/ckey/contract/" in loc
