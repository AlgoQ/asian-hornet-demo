from fastapi import FastAPI
from config import setup_cors
from routers import observations, photos
from create_tables import create_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Setup CORS after initializing the app
setup_cors(app)

# Include your routers
app.include_router(observations.router)
app.include_router(photos.router)
