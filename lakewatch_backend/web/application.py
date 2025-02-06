from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from lakewatch_backend.log import configure_logging
from lakewatch_backend.web.api.router import api_router
from lakewatch_backend.web.lifespan import lifespan_setup


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    configure_logging()
    app = FastAPI(
        title="lakewatch_backend",
        version=metadata.version("lakewatch_backend"),
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
