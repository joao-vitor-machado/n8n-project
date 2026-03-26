import calendar
import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Client, ConsumptionReading, Contract
from schema.schema_validator import validate_payload


def _add_months(base: date, delta_months: int) -> date:
    y, m = base.year, base.month + delta_months
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    last = calendar.monthrange(y, m)[1]
    return date(y, m, min(base.day, last))


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

    @staticmethod
    def analyze_client_reading_outliers(
        session: Session,
        months: int,
        *,
        as_of: date | None = None,
    ) -> dict[str, Any]:
        if months < 1:
            raise ValueError("months must be at least 1")

        end = as_of if as_of is not None else date.today()
        start = _add_months(end, -months)

        stmt = (
            select(
                ConsumptionReading,
                Contract.contract_key,
                Client.client_key,
                Client.name,
            )
            .join(Contract, ConsumptionReading.contract_id == Contract.id)
            .join(Client, Contract.client_id == Client.id)
            .where(
                Contract.active.is_(True),
                ConsumptionReading.reading_date >= start,
                ConsumptionReading.reading_date <= end,
            )
            .order_by(Client.client_key, ConsumptionReading.reading_date)
        )
        rows = session.execute(stmt).all()

        by_client: dict[str, dict[str, Any]] = {}
        all_values: list[float] = []
        for reading, contract_key, client_key, name in rows:
            value = float(reading.reading_value)
            if client_key not in by_client:
                by_client[client_key] = {
                    "name": name,
                    "items": [],
                }
            by_client[client_key]["items"].append((reading, contract_key, value))
            all_values.append(value)

        base_average = (sum(all_values) / len(all_values)) if all_values else None

        clients_out: list[dict[str, Any]] = []
        outlier_clients: list[dict[str, Any]] = []
        for client_key in sorted(by_client.keys()):
            entry = by_client[client_key]
            items: list[tuple[ConsumptionReading, str, float]] = entry["items"]
            values = [value for _, _, value in items]
            client_average = (sum(values) / len(values)) if values else None
            is_outlier = (
                base_average is not None
                and client_average is not None
                and client_average > base_average
            )
            sample = [
                {
                    "reading_key": reading.reading_key,
                    "contract_key": contract_key,
                    "reading_date": str(reading.reading_date),
                    "reading_value": value,
                }
                for reading, contract_key, value in items
            ]

            payload = {
                "client_key": client_key,
                "name": entry["name"],
                "reading_count": len(items),
                "average_consumption": client_average,
                "outlier": is_outlier,
                "readings": sample,
            }
            clients_out.append(payload)
            if is_outlier:
                outlier_clients.append(payload)

        return {
            "period": {
                "months": months,
                "start_date": str(start),
                "end_date": str(end),
            },
            "base_average_consumption": base_average,
            "outlier_count": len(outlier_clients),
            "outliers": outlier_clients,
            "clients": clients_out,
        }
