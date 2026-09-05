import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

from api.routes import router as api_router

app = FastAPI(
    title="GREENLIGHT: Autonomous Pre-Production Script Clearance & Risk Copilot",
    description="Multi-agent legal and E&O clearance engine powered by Google ADK & Parallel Web MCP.",
    version="1.0.0"
)

# Enable CORS for local and production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(api_router)

# Mount static frontend
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_dashboard():
    """Serves the cinematic single-page studio dashboard."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "GREENLIGHT API is online. Static dashboard index.html not yet built."}


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "service": "greenlight-clearance-copilot",
        "mcp_target": "https://search-mcp.parallel.ai/mcp"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
