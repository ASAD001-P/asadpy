from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import engine
from app.routers import auth, products

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(title="Production FastAPI Store", lifespan=lifespan)

# Include Routers
app.include_router(auth.router)
app.include_router(products.router)
