from importlib import metadata
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from lakewatch.log import configure_logging
from lakewatch.web.router import api_router
from lakewatch.web.lifespan import lifespan_setup

def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: FastAPI application instance.
    """
    configure_logging()

    try:
        app_version = metadata.version("lakewatch")
    except metadata.PackageNotFoundError:
        app_version = "0.1.0"  # Fallback version

    app = FastAPI(
        title="LakeWatch API",
        version=app_version,
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,   
    )

    # Enable CORS (important if frontend is hosted separately)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change to specific domain in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(router=api_router, prefix="/api")

    return app
