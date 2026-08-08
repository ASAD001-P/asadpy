from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine
from app.routers import auth, products

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(title="Production FastAPI Store", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin (e.g., local React/Next apps, Vercel, Netlify)
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],  # Allows Bearer tokens and custom headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to AsadPy API! Visit /docs for interactive documentation."}

# Include Routers
app.include_router(auth.router)
app.include_router(products.router)
