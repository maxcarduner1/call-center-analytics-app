from fastapi import FastAPI
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
from services.lakebase import Lakebase

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Call Center Analytics App",
    description="A simple FastAPI application",
    version="1.0.0",
)


@app.get("/")
async def read_root():
    """Serve the index.html file."""
    try:
        return FileResponse("frontend/index.html")
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/test-db")
async def test_db():
    """Test the Lakebase connection by querying the current time."""
    try:
        lakebase = Lakebase()
        rows = lakebase.query("SELECT NOW();")
        
        if rows and len(rows) > 0:
            return {
                "success": True,
                "timestamp": str(rows[0][0])
            }
        else:
            return {
                "success": False,
                "error": "No results returned"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
