import falcon
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from controller import ContractController
from database import session_scope
from dto import ContractDTO
from models import Client, Contract


class ContractCollectionResource:
    def on_get(self, _req, resp, client_key):
        with session_scope() as session:
            client = session.scalars(select(Client).where(Client.client_key == client_key)).first()
            if client is None:
                raise falcon.HTTPNotFound(
                    title="Not found",
                    description="Unknown client_key.",
                )
            rows = session.scalars(
                select(Contract)
                .where(Contract.client_id == client.id)
                .options(selectinload(Contract.client))
                .order_by(Contract.id)
            ).all()
        resp.media = {"items": [ContractDTO.contract_to_dict(c) for c in rows]}

    def on_post(self, req, resp, client_key):
        try:
            body = req.media
        except falcon.MediaNotFoundError:
            body = None
        if not isinstance(body, dict):
            raise falcon.HTTPBadRequest(
                title="Invalid body",
                description="Expected a JSON object with start_date and active.",
            )
        try:
            with session_scope() as session:
                contract, client = ContractController.create_contract(session, client_key, body)
        except ValueError as e:
            raise falcon.HTTPBadRequest(title="Validation error", description=str(e))
        except IntegrityError:
            raise falcon.HTTPConflict(
                title="Duplicate contract",
                description="A contract with this contract_key already exists.",
            )
        resp.status = falcon.HTTP_201
        resp.location = (
            f"/v1/client/{client.client_key}/contract/{contract.contract_key}"
        )
        resp.media = ContractDTO.contract_to_dict(contract, client=client)
