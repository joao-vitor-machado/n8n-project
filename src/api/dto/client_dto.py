from models import Client

class ClientDTO:
    @staticmethod
    def client_to_dict(row: Client) -> dict:
        return {
            "client_key": row.client_key,
            "document_number": row.document_number,
            "name": row.name,
        }