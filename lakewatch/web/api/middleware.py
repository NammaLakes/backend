from fastapi import Request, HTTPException
from lakewatch.web.api.auth import validate_api_key

async def api_key_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return await call_next(request)
