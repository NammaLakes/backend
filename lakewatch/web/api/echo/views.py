from fastapi import APIRouter
from .schema import EchoRequest, EchoResponse

echo_router = APIRouter()

@echo_router.post("/", response_model=EchoResponse)
async def echo_message(request: EchoRequest):
    return {"response": f"Echo: {request.message}"}
