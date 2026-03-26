from sqlalchemy import text

from src.database import session_scope


def check_database() -> bool:
    with session_scope() as session:
        session.execute(text("SELECT 1"))
    return True


def health_payload() -> dict:
    try:
        check_database()
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": "up" if db_ok else "down"}


class HealthResource:
    def on_get(self, _req, resp):
        resp.media = health_payload()
