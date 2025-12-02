from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import sys

from app.database import init_db
from app.routers import auth, rides, drivers, cars, payments

# Настройка логирования для Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Не падаем при ошибке БД - дадим сервису запуститься
        # и показать ошибку через API
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="Taxi Service API",
    description="API для службы такси с авторизацией через JWT",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(rides.router, prefix="/rides", tags=["Rides"])
app.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
app.include_router(cars.router, prefix="/cars", tags=["Cars"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Taxi Service API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint для Cloud Run startup probe
    """
    return {"status": "ok"}
