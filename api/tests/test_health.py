from contextlib import contextmanager
from unittest.mock import MagicMock

from falcon import HTTP_200


@contextmanager
def _session_scope_ok():
    s = MagicMock()
    s.execute = MagicMock()
    yield s


@contextmanager
def _session_scope_fail():
    s = MagicMock()

    def boom(*_a, **_k):
        raise ConnectionError("database unavailable")

    s.execute.side_effect = boom
    yield s


def test_get_health_ok(client, monkeypatch):
    monkeypatch.setattr("resources.health.session_scope", _session_scope_ok)
    result = client.simulate_get("/health")
    assert result.status == HTTP_200
    assert result.json == {"status": "ok", "database": "up"}


def test_get_health_degraded_when_db_fails(client, monkeypatch):
    monkeypatch.setattr("resources.health.session_scope", _session_scope_fail)
    result = client.simulate_get("/health")
    assert result.status == HTTP_200
    assert result.json == {"status": "degraded", "database": "down"}
