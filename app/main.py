from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import auth, rides, drivers, cars, payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


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
