import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Client, ConsumptionReading, Contract
from schema.schema_validator import validate_payload


class ReadingController:
    @staticmethod
    def _validate_create_payload(body: dict[str, Any]) -> tuple[str, str, date, Decimal]:
        validate_payload(body, "post_reading.json")

        reading_date = date.fromisoformat(body["reading_date"].strip())
        reading_value = Decimal(str(body["reading_value"]))
        raw_key = body.get("reading_key")
        if raw_key is None or raw_key == "":
            reading_key = str(uuid.uuid4())
        else:
            reading_key = raw_key.strip()
        return reading_key, reading_date, reading_value

    @staticmethod
    def create_reading(
        session: Session, client_key: str, contract_key: str, body: dict[str, Any]
    ) -> tuple[ConsumptionReading, Contract]:
        reading_key, reading_date, reading_value = (
            ReadingController._validate_create_payload(body)
        )

        client = session.scalars(select(Client).where(Client.client_key == client_key)).first()
        if client is None:
            raise ValueError(f"Unknown client_key: {client_key!r}")
        contract = session.scalars(
            select(Contract)
            .where(Contract.contract_key == contract_key)
            .options(selectinload(Contract.client))
        ).first()
        if contract is None:
            raise ValueError(f"Unknown contract_key: {contract_key!r}")
        if contract.client_id != client.id:
            raise ValueError("Contract does not belong to this client.")

        reading = ConsumptionReading(
            reading_key=reading_key,
            contract_id=contract.id,
            reading_date=reading_date,
            reading_value=reading_value,
        )
        session.add(reading)
        session.flush()
        return reading, contract
