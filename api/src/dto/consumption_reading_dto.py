from src.models import ConsumptionReading

from src.dto.contract_dto import ContractDTO


class ConsumptionReadingDTO:
    @staticmethod
    def reading_to_dict(row: ConsumptionReading) -> dict:
        return {
            "reading_key": row.reading_key,
            "contract": ContractDTO.contract_to_dict(row.contract),
            "reading_date": str(row.reading_date),
            "reading_value": float(row.reading_value),
        }
