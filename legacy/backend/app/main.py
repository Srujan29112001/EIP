"""
Main FastAPI application
Entrepreneurship Intelligence Platform
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from .core.config import settings
from .core.logging import setup_logging, get_logger
from .api.v1 import api_router
from .models.database import engine, Base

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} - {settings.APP_ENV}")
    logger.info("Creating database tables...")

    # Create all database tables
    Base.metadata.create_all(bind=engine)

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Decision-Making System for Entrepreneurs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = (time.time() - start_time) * 1000

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.2f}ms"
    )

    # Add custom header
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
        "environment": settings.APP_ENV
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "timestamp": time.time()
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge
        from starlette.responses import Response

        # Basic metrics (these would ideally be defined at module level for persistence)
        # For now, return a simple metrics format
        metrics_text = f"""# HELP eip_requests_total Total number of requests
# TYPE eip_requests_total counter
eip_requests_total {{method="GET",endpoint="/health"}} 0

# HELP eip_request_duration_seconds Request duration in seconds
# TYPE eip_request_duration_seconds histogram
eip_request_duration_seconds_bucket {{le="0.1"}} 0

# HELP eip_active_users Active users gauge
# TYPE eip_active_users gauge
eip_active_users {{tier="aspiring"}} 0
"""
        return Response(content=metrics_text, media_type="text/plain")
    except ImportError:
        # Prometheus client not installed, return basic info
        return {
            "metrics_format": "prometheus",
            "note": "Install prometheus-client for full metrics: pip install prometheus-client",
            "status": "basic_metrics_available"
        }


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.API_WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
