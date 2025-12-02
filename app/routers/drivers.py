from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Driver, User
from app.schemas import DriverCreate, DriverResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver: DriverCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать нового водителя
    """
    # Check if license number exists
    result = await db.execute(
        select(Driver).where(Driver.license_number == driver.license_number)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License number already registered"
        )
    
    db_driver = Driver(
        name=driver.name,
        phone=driver.phone,
        license_number=driver.license_number
    )
    db.add(db_driver)
    await db.commit()
    await db.refresh(db_driver)
    return db_driver


@router.get("/", response_model=List[DriverResponse])
async def get_drivers(
    skip: int = 0,
    limit: int = 10,
    available_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список водителей
    """
    query = select(Driver)
    if available_only:
        query = query.where(Driver.is_available == True)
    
    result = await db.execute(query.offset(skip).limit(limit))
    drivers = result.scalars().all()
    return drivers


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о конкретном водителе
    """
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    return driver
