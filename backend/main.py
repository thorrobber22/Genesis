"""
FastAPI Main Application
Date: 2025-06-14 18:01:07 UTC
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Import routes
from backend.api.routes import router as api_router

# Create app
app = FastAPI(
    title="Hedge Intelligence API",
    version="1.0.0",
    description="IPO Intelligence Platform"
)

# Include API routes with /api prefix
app.include_router(api_router, prefix="/api")

# Mount static files
static_path = Path("frontend/static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
else:
    # Try alternative path
    static_path = Path("static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Serve index.html at root
@app.get("/")
async def read_index():
    index_path = Path("frontend/index.html")
    if not index_path.exists():
        index_path = Path("index.html")
    
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        return {"error": "Frontend not found"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Debug endpoint to check data
@app.get("/debug/data")
async def debug_data():
    """Check what data files exist"""
    data_dir = Path("data")
    files = []
    
    if data_dir.exists():
        for file in data_dir.glob("*.json"):
            files.append(file.name)
    
    return {
        "data_files": files,
        "data_dir_exists": data_dir.exists()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
