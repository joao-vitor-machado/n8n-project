import falcon
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from controller import ClientController
from database import session_scope
from dto import ClientDTO
from models import Client


class ClientCollectionResource:
    def on_get(self, _req, resp):
        with session_scope() as session:
            rows = session.scalars(select(Client).order_by(Client.id)).all()
        resp.media = {"items": [ClientDTO.client_to_dict(c) for c in rows]}

    def on_post(self, req, resp):
        try:
            body = req.media
        except falcon.MediaNotFoundError:
            body = None
        if not isinstance(body, dict):
            raise falcon.HTTPBadRequest(
                title="Invalid body",
                description="Expected a JSON object with name and document_number.",
            )
        try:
            with session_scope() as session:
                client = ClientController.create_client(session, body)
        except ValueError as e:
            raise falcon.HTTPBadRequest(title="Validation error", description=str(e))
        except IntegrityError:
            raise falcon.HTTPConflict(
                title="Duplicate client",
                description="A client with this client_key or document_number already exists.",
            )
        resp.status = falcon.HTTP_201
        resp.location = f"/v1/client/{client.client_key}"
        resp.media = ClientDTO.client_to_dict(client)
