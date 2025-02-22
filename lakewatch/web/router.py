from fastapi import APIRouter
from lakewatch.web.api.monitoring.views import router as monitoring_router

api_router = APIRouter()

# Include the monitoring API routes
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
