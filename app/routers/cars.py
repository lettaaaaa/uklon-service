from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Car, Driver, User
from app.schemas import CarCreate, CarResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(
    car: CarCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавить новый автомобиль
    """
    # Check if driver exists
    result = await db.execute(select(Driver).where(Driver.id == car.driver_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Check if plate number exists
    result = await db.execute(
        select(Car).where(Car.plate_number == car.plate_number)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plate number already registered"
        )
    
    db_car = Car(
        driver_id=car.driver_id,
        model=car.model,
        plate_number=car.plate_number,
        color=car.color,
        year=car.year
    )
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    return db_car


@router.get("/", response_model=List[CarResponse])
async def get_cars(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список автомобилей
    """
    result = await db.execute(
        select(Car).offset(skip).limit(limit)
    )
    cars = result.scalars().all()
    return cars


@router.get("/{car_id}", response_model=CarResponse)
async def get_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о конкретном автомобиле
    """
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    return car
