from importlib import metadata
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles

from lakewatch.web.api.router import api_router
from lakewatch.web.lifespan import lifespan

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="lakewatch",
        version=metadata.version("lakewatch"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
        lifespan=lifespan,
    )

    app.include_router(router=api_router, prefix="/api")

    return app
