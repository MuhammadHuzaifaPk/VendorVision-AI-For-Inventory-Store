import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.config import settings
from api.routes import router as api_router
from models.schemas import HealthCheckResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        ai_engine_active=settings.is_ai_configured(),
    )

# Robust path resolution for frontend static files
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

CSS_DIR = FRONTEND_DIR / "css"
JS_DIR = FRONTEND_DIR / "js"

# Mount static subdirectories
if CSS_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(CSS_DIR)), name="css")

if JS_DIR.exists():
    app.mount("/js", StaticFiles(directory=str(JS_DIR)), name="js")

# Serve main single-page application
@app.get("/", tags=["Root"])
async def serve_frontend():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "error": "Frontend index.html not found",
        "checked_path": str(index_file)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)