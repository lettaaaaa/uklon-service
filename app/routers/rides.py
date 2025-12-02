from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Ride, User
from app.schemas import RideCreate, RideResponse, RideUpdate
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride(
    ride: RideCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новую поездку
    """
    db_ride = Ride(
        user_id=current_user.id,
        pickup_location=ride.pickup_location,
        dropoff_location=ride.dropoff_location,
        status="pending"
    )
    db.add(db_ride)
    await db.commit()
    await db.refresh(db_ride)
    return db_ride


@router.get("/", response_model=List[RideResponse])
async def get_rides(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список поездок текущего пользователя
    """
    result = await db.execute(
        select(Ride)
        .where(Ride.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    rides = result.scalars().all()
    return rides


@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детали конкретной поездки
    """
    result = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = result.scalar_one_or_none()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this ride"
        )
    
    return ride


@router.patch("/{ride_id}", response_model=RideResponse)
async def update_ride(
    ride_id: int,
    ride_update: RideUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить информацию о поездке (статус, водитель, цена)
    """
    result = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = result.scalar_one_or_none()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ride"
        )
    
    if ride_update.driver_id is not None:
        ride.driver_id = ride_update.driver_id
    if ride_update.status is not None:
        ride.status = ride_update.status
        if ride_update.status == "completed":
            ride.completed_at = datetime.utcnow()
    if ride_update.price is not None:
        ride.price = ride_update.price
    
    await db.commit()
    await db.refresh(ride)
    return ride


@router.delete("/{ride_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_ride(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Отменить поездку
    """
    result = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = result.scalar_one_or_none()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this ride"
        )
    
    ride.status = "cancelled"
    await db.commit()
    return None
