from models import ConsumptionReading, Contract

from .contract_dto import ContractDTO


class ConsumptionReadingDTO:
    @staticmethod
    def reading_to_dict(
        row: ConsumptionReading, *, contract: Contract | None = None
    ) -> dict:
        ctr = contract if contract is not None else row.contract
        return {
            "reading_key": row.reading_key,
            "contract": ContractDTO.contract_to_dict(ctr),
            "reading_date": str(row.reading_date),
            "reading_value": float(row.reading_value),
        }
