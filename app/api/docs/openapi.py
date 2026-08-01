from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def configure_openapi(
    app: FastAPI,
) -> None:

    def custom_openapi():

        if app.openapi_schema:

            return app.openapi_schema

        openapi_schema = get_openapi(
            title="SikaGlé API",
            version="1.0.0",
            summary=(
                "API publique V1 de SikaGlé"
            ),
            description=(
                "API REST officielle permettant "
                "d'interagir avec la plateforme "
                "SikaGlé."
            ),
            routes=app.routes,
        )

        openapi_schema["info"][
            "contact"
        ] = {
            "name": "SikaGlé",
        }

        app.openapi_schema = (
            openapi_schema
        )

        return app.openapi_schema

    app.openapi = custom_openapi
