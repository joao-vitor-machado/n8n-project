import falcon
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from controller import ReadingController
from database import session_scope
from dto import ConsumptionReadingDTO
from models import Client, ConsumptionReading, Contract


class ReadingCollectionResource:
    def on_get(self, _req, resp, client_key, contract_key):
        with session_scope() as session:
            client = session.scalars(select(Client).where(Client.client_key == client_key)).first()
            if client is None:
                raise falcon.HTTPNotFound(
                    title="Not found",
                    description="Unknown client_key.",
                )
            contract = session.scalars(
                select(Contract)
                .where(Contract.contract_key == contract_key, Contract.client_id == client.id)
                .options(selectinload(Contract.client))
            ).first()
            if contract is None:
                raise falcon.HTTPNotFound(
                    title="Not found",
                    description="Unknown contract for this client.",
                )
            rows = session.scalars(
                select(ConsumptionReading)
                .where(ConsumptionReading.contract_id == contract.id)
                .options(
                    selectinload(ConsumptionReading.contract).selectinload(Contract.client)
                )
                .order_by(ConsumptionReading.id)
            ).all()
        resp.media = {"items": [ConsumptionReadingDTO.reading_to_dict(r) for r in rows]}

    def on_post(self, req, resp, client_key, contract_key):
        try:
            body = req.media
        except falcon.MediaNotFoundError:
            body = None
        if not isinstance(body, dict):
            raise falcon.HTTPBadRequest(
                title="Invalid body",
                description=(
                    "Expected a JSON object with reading_date and reading_value."
                ),
            )
        try:
            with session_scope() as session:
                reading, contract = ReadingController.create_reading(session, client_key, contract_key, body)
        except ValueError as e:
            raise falcon.HTTPBadRequest(title="Validation error", description=str(e))
        except IntegrityError:
            raise falcon.HTTPConflict(
                title="Duplicate reading",
                description="A reading with this reading_key already exists.",
            )
        resp.status = falcon.HTTP_201
        resp.location = (
            f"/v1/client/{client_key}/contract/{contract_key}/reading/"
            f"{reading.reading_key}"
        )
        resp.media = ConsumptionReadingDTO.reading_to_dict(reading, contract=contract)
