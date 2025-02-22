from fastapi import FastAPI
from lakewatch.web.router import api_router  # Ensure the correct import path

# Initialize FastAPI app
app = FastAPI(title="Lake Monitoring API", version="1.0")

# Register API routes with the correct prefix
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lakewatch.web.main:app", host="0.0.0.0", port=8000, reload=True)
