from src.models import Contract

from .client_dto import ClientDTO

class ContractDTO:
    @staticmethod
    def contract_to_dict(row: Contract) -> dict:
        return {
            "contract_key": row.contract_key,
            "client": ClientDTO.client_to_dict(row.client),
            "start_date": str(row.start_date),
            "active": row.active,
        }
