from fastapi import FastAPI
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

from routers.calls import router as calls_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Call Center Analytics App",
    description="Call Quality Scoring viewer with AI-generated quality assessments",
    version="1.0.0",
)

# Include routers
app.include_router(calls_router)


@app.get("/")
async def read_root():
    """Serve the index.html file."""
    try:
        return FileResponse("frontend/index.html")
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
