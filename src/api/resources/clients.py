from sqlalchemy import select

from database import session_scope
from models import Client
from dto import ClientDTO


class ClientCollectionResource:
    def on_get(self, _req, resp):
        with session_scope() as session:
            rows = session.scalars(select(Client).order_by(Client.id)).all()
        resp.media = {"items": [ClientDTO.client_to_dict(c) for c in rows]}
