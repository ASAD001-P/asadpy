import asyncio
import logging
from contextlib import asynccontextmanager

from arq.worker import Worker
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlmodel import select

from app.core.config import settings
from app.core.database import engine
from app.routers import auth, products
from app.worker import WorkerSettings  # 👈 Imports worker functions & redis settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("asadpy")

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI Store application...")

    # 1. Initialize Redis Cache
    try:
        redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        logger.info("Redis cache initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")

    # 2. 🚀 Start Embedded ARQ Worker in the background ($0/month)
    try:
        worker = Worker(
            functions=WorkerSettings.functions,
            redis_settings=WorkerSettings.redis_settings
        )
        asyncio.create_task(worker.async_run())
        logger.info("Embedded ARQ Background Worker started successfully.")
    except Exception as e:
        logger.warning(f"Failed to start embedded ARQ Worker: {e}")

    yield

    logger.info("Shutting down and disposing database engine...")
    await engine.dispose()


app = FastAPI(title="Production FastAPI Store", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Welcome to AsadPy API! Visit /docs for interactive documentation."}


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def health_check():
    try:
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