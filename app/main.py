import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlmodel import select

from app.core.database import engine, get_session
from app.routers import auth, products

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("asadpy")

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI Store application...")
    yield
    logger.info("Shutting down and disposing database engine...")
    await engine.dispose()

app = FastAPI(title="Production FastAPI Store", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin (e.g., local React/Next apps, Vercel, Netlify)
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],  # Allows Bearer tokens and custom headers
)

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Welcome to AsadPy API! Visit /docs for interactive documentation."}

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def health_check():
    try:
        # Ping the database to ensure active connectivity
        async with engine.connect() as conn:
            await conn.execute(select(1))
        return {
            "status": "healthy",
            "database": "connected",
            "service": "asadpy-api"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )
    
# Include Routers
app.include_router(auth.router)
app.include_router(products.router)
