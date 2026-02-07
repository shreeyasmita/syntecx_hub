from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
from app.core.config import settings
from app.core.logging import logger
from app.api.v1.api import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s"
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Exception handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error": True}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": True}
        )
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting SynTeCX House Price Prediction API")
        logger.info(f"API Version: {settings.VERSION}")
        logger.info(f"Debug Mode: {settings.DEBUG}")
        
        # Initialize services here
        # await init_db()
        # await init_redis()
        # await load_ml_models()
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down SynTeCX House Price Prediction API")
        # Cleanup resources here
    
    return app


app = create_app()