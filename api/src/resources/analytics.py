import falcon

from controller import ReadingController
from database import session_scope


class ReadingOutliersResource:
    def on_get(self, req, resp):
        months = req.get_param_as_int("months")
        if months is None:
            months = 3
        if months < 1:
            raise falcon.HTTPBadRequest(
                title="Invalid months",
                description="Query parameter months must be a positive integer.",
            )
        try:
            with session_scope() as session:
                payload = ReadingController.analyze_client_reading_outliers(session, months)
        except ValueError as e:
            raise falcon.HTTPBadRequest(title="Validation error", description=str(e))
        resp.media = payload
