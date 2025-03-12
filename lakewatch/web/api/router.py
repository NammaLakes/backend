from fastapi.routing import APIRouter

from lakewatch.web.api import echo, monitoring
from lakewatch.web.api.get_data import router as get_data_router

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(get_data_router, prefix="/get_data", tags=["get_data"])
