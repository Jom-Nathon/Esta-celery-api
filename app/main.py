from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import plots
from app.db.database import create_db_and_tables
from app.core.config import settings
from app.celery_worker import celery

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # Shutdown logic
    celery.control.purge()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    lifespan=lifespan
)

# Include router
app.include_router(plots.router, prefix=settings.API_STR) 
