import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Client, Contract
from schema.schema_validator import validate_payload


class ContractController:
    @staticmethod
    def _validate_create_payload(body: dict[str, Any]) -> tuple[str, str, date, bool]:
        validate_payload(body, "post_contract.json")

        start_date = date.fromisoformat(body["start_date"].strip())
        active = body["active"]
        raw_key = body.get("contract_key")
        if raw_key is None or raw_key == "":
            contract_key = str(uuid.uuid4())
        else:
            contract_key = raw_key.strip()
        return contract_key, start_date, active

    @staticmethod
    def create_contract(session: Session, client_key: str, body: dict[str, Any]) -> tuple[Contract, Client]:
        contract_key,start_date, active = ContractController._validate_create_payload(
            body
        )
        client = session.scalars(select(Client).where(Client.client_key == client_key)).first()
        if client is None:
            raise ValueError(f"Unknown client_key: {client_key!r}")

        contract = Contract(
            contract_key=contract_key,
            client_id=client.id,
            start_date=start_date,
            active=active,
        )
        session.add(contract)
        session.flush()
        return contract, client
