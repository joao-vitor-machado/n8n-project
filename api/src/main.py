import falcon

from src.resources.clients import ClientCollectionResource
from src.resources.health import HealthResource


def create_app() -> falcon.App:
    app = falcon.App()
    app.add_route("/health", HealthResource())
    app.add_route("/v1/clients", ClientCollectionResource())
    return app


app = create_app()
