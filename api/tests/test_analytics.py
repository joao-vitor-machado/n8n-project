from contextlib import contextmanager
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from falcon import HTTP_200, HTTP_400

from controller.reading_controller import ReadingController


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class FakeExecuteSession:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, _stmt):
        return _FakeResult(self._rows)


def _reading(key, value, d):
    return SimpleNamespace(
        reading_key=key,
        reading_value=Decimal(str(value)),
        reading_date=d,
    )


def test_get_reading_outliers_rejects_non_positive_months(client):
    result = client.simulate_get("/v1/analytics/reading-outliers?months=0")
    assert result.status == HTTP_400


def test_analyze_empty_window():
    session = FakeExecuteSession([])
    out = ReadingController.analyze_client_reading_outliers(
        session, 6, as_of=date(2025, 6, 30)
    )
    assert out["clients"] == []
    assert out["outliers"] == []
    assert out["base_average_consumption"] is None
    assert out["period"]["months"] == 6
    assert out["period"]["end_date"] == "2025-06-30"


def test_analyze_marks_client_average_above_base_as_outlier():
    as_of = date(2025, 6, 30)
    rows = [
        (_reading("a1", 80, as_of), "c1", "client-a", "A"),
        (_reading("a2", 90, as_of), "c1", "client-a", "A"),
        (_reading("b1", 200, as_of), "c2", "client-b", "B"),
        (_reading("b2", 220, as_of), "c2", "client-b", "B"),
    ]
    out = ReadingController.analyze_client_reading_outliers(
        FakeExecuteSession(rows), 12, as_of=as_of
    )
    assert len(out["clients"]) == 2
    assert out["base_average_consumption"] == 147.5
    assert out["outlier_count"] == 1
    assert out["outliers"][0]["client_key"] == "client-b"
    assert out["outliers"][0]["average_consumption"] == 210.0


def test_analyze_single_client_not_outlier():
    as_of = date(2025, 6, 30)
    rows = [
        (_reading("r1", 10, as_of), "c1", "client-a", "A"),
        (_reading("r2", 20, as_of), "c1", "client-a", "A"),
    ]
    out = ReadingController.analyze_client_reading_outliers(
        FakeExecuteSession(rows), 3, as_of=as_of
    )
    assert out["clients"][0]["reading_count"] == 2
    assert out["clients"][0]["outlier"] is False
    assert out["outliers"] == []


def test_get_reading_outliers_ok(client, monkeypatch):
    d0 = date.today()
    rows = [
        (_reading("r1", 50, d0), "c1", "client-a", "Acme"),
        (_reading("r2", 60, d0), "c1", "client-a", "Acme"),
        (_reading("r3", 150, d0), "c2", "client-b", "Umbrella"),
        (_reading("r4", 160, d0 - timedelta(days=1)), "c2", "client-b", "Umbrella"),
    ]
    fake = FakeExecuteSession(rows)

    @contextmanager
    def fake_session_scope():
        yield fake

    monkeypatch.setattr("resources.analytics.session_scope", fake_session_scope)

    result = client.simulate_get("/v1/analytics/reading-outliers?months=6")
    assert result.status == HTTP_200
    body = result.json
    assert body["period"]["months"] == 6
    assert len(body["clients"]) == 2
    assert body["outlier_count"] == 1
    assert len(body["outliers"]) == 1
    assert body["outliers"][0]["client_key"] == "client-b"
    client_flags = {c["client_key"]: c["outlier"] for c in body["clients"]}
    assert client_flags["client-a"] is False
    assert client_flags["client-b"] is True
