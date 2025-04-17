from fastapi.routing import APIRouter

from lakewatch.web.api import monitoring
from lakewatch.web.api.get_data import router as get_data_router
from lakewatch.web.api.monitoring import router as ws_router

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(get_data_router, prefix="/get_data", tags=["get_data"])
api_router.include_router(ws_router, prefix="/monitoring", tags=["WebSockets"])
