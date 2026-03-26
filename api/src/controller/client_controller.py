import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.models import Client
from src.schema.schema_validator import validate_payload


class ClientController:
    @staticmethod
    def _validate_create_payload(body: dict[str, Any]) -> tuple[str, str, str]:
        validate_payload(body, "post_client.json")

        name = body["name"].strip()
        document_number = body["document_number"].strip()
        raw_key = body.get("client_key")
        if raw_key is None or raw_key == "":
            client_key = str(uuid.uuid4())
        else:
            client_key = raw_key.strip()
        return client_key, document_number, name


    @staticmethod
    def create_client(session: Session, body: dict[str, Any]) -> Client:

        client_key, document_number, name = ClientController._validate_create_payload(body)
        client = Client(
            client_key=client_key,
            document_number=document_number,
            name=name,
        )
        session.add(client)
        session.flush()
        return client

