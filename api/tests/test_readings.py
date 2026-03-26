from contextlib import contextmanager
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

from falcon import HTTP_200, HTTP_201, HTTP_400


def _scope_factory(session):
    @contextmanager
    def _scope():
        yield session

    return _scope

def test_get_readings_empty_list(client, monkeypatch):
    client_row = SimpleNamespace(
        id=1,
        client_key="ck",
        document_number="12345678901234",
        name="Acme",
    )
    contract_row = SimpleNamespace(
        id=10,
        contract_key="ctr1",
        client_id=1,
        start_date=date(2024, 1, 1),
        active=True,
        client=client_row,
    )
    m_client = MagicMock()
    m_client.first.return_value = client_row
    m_contract = MagicMock()
    m_contract.first.return_value = contract_row
    m_readings = MagicMock()
    m_readings.all.return_value = []
    mock_session = MagicMock()
    mock_session.scalars.side_effect = [m_client, m_contract, m_readings]
    monkeypatch.setattr("resources.readings.session_scope", _scope_factory(mock_session))

    result = client.simulate_get("/v1/client/ck/contract/ctr1/reading")

    assert result.status == HTTP_200
    assert result.json == {"items": []}


def test_post_readings_unknown_contract(client, monkeypatch):
    mock_session = MagicMock()
    client_row = SimpleNamespace(
        id=1,
        client_key="ck",
        document_number="12345678901234",
        name="Acme",
    )
    m_client = MagicMock()
    m_client.first.return_value = client_row
    m_contract = MagicMock()
    m_contract.first.return_value = None
    mock_session.scalars.side_effect = [m_client, m_contract]
    monkeypatch.setattr("resources.readings.session_scope", _scope_factory(mock_session))

    result = client.simulate_post(
        "/v1/client/ck/contract/badctr/reading",
        json={
            "reading_date": "2024-06-15",
            "reading_value": 123.45,
        },
    )

    assert result.status == HTTP_400
    assert "contract_key" in (result.json or {}).get("description", "").lower()


def test_post_readings_created(client, monkeypatch):
    mock_session = MagicMock()
    client_row = SimpleNamespace(
        id=1,
        client_key="ck",
        document_number="12345678901234",
        name="Acme",
    )
    contract_row = SimpleNamespace(
        id=10,
        contract_key="ctr1",
        client_id=1,
        start_date=date(2024, 1, 1),
        active=True,
        client=client_row,
    )
    scalars_result = MagicMock()
    scalars_result.first.side_effect = [client_row, contract_row]
    mock_session.scalars.return_value = scalars_result
    monkeypatch.setattr("resources.readings.session_scope", _scope_factory(mock_session))

    result = client.simulate_post(
        "/v1/client/ck/contract/ctr1/reading",
        json={
            "reading_date": "2024-07-01",
            "reading_value": 99.5,
        },
    )

    assert result.status == HTTP_201
    assert result.json["reading_date"] == "2024-07-01"
    assert result.json["reading_value"] == 99.5
    assert result.json["contract"]["contract_key"] == "ctr1"
    assert len(result.json["reading_key"]) == 36
    loc = result.headers.get("Location", "")
    assert loc.endswith(result.json["reading_key"])
    assert "/v1/client/ck/contract/ctr1/reading/" in loc
