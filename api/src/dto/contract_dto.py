from models import Client, Contract

from .client_dto import ClientDTO


class ContractDTO:
    @staticmethod
    def contract_to_dict(row: Contract, *, client: Client | None = None) -> dict:
        c = client if client is not None else row.client
        return {
            "contract_key": row.contract_key,
            "client": ClientDTO.client_to_dict(c),
            "start_date": str(row.start_date),
            "active": row.active,
        }
