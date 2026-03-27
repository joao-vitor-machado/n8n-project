import falcon
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from controller import ClientController, ReadingController
from database import session_scope
from dto import ClientDTO
from models import Client
from falcon import Request, Response

class ClientCollectionResource:
    def on_get(self, req: Request, resp: Response, client_key: str | None = None):
        if client_key is None:
            with session_scope() as session:
                rows = session.scalars(select(Client).order_by(Client.id)).all()
            resp.media = {"items": [ClientDTO.client_to_dict(c) for c in rows]}
            return

        months = req.get_param_as_int("months", default=3)
        if months < 1:
            raise falcon.HTTPBadRequest(title="Invalid months", description="Query parameter months must be a positive integer.")
        try:
            with session_scope() as session:
                payload = ReadingController.get_client_consumption_insight(
                    session, client_key, months
                )
        except ValueError as e:
            msg = str(e)
            if msg.startswith("Unknown client_key"):
                raise falcon.HTTPNotFound(
                    title="Not found",
                    description=msg,
                )
            raise falcon.HTTPBadRequest(title="Validation error", description=msg)
        resp.media = payload

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
