import falcon

from resources.analytics import ReadingOutliersResource
from resources.clients import ClientCollectionResource
from resources.contracts import ContractCollectionResource
from resources.health import HealthResource
from resources.readings import ReadingCollectionResource


def create_app() -> falcon.App:
    app = falcon.App()
    app.add_route("/health", HealthResource())
    client_resource = ClientCollectionResource()
    app.add_route(
        "/v1/client", 
        client_resource
    )
    
    contract_resource = ContractCollectionResource()
    app.add_route(
        "/v1/client/{client_key}/contract", 
        contract_resource
    )
    reading_resource = ReadingCollectionResource()
    app.add_route(
        "/v1/client/{client_key}/contract/{contract_key}/reading", 
        reading_resource
    )
    app.add_route("/v1/analytics/reading-outliers", ReadingOutliersResource())

    return app


app = create_app()
