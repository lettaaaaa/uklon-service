from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Payment, Ride, User
from app.schemas import PaymentCreate, PaymentResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новый платеж
    """
    # Check if ride exists and belongs to user
    result = await db.execute(select(Ride).where(Ride.id == payment.ride_id))
    ride = result.scalar_one_or_none()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this ride"
        )
    
    # Check if payment already exists for this ride
    result = await db.execute(
        select(Payment).where(Payment.ride_id == payment.ride_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this ride"
        )
    
    db_payment = Payment(
        ride_id=payment.ride_id,
        user_id=current_user.id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        status="completed"
    )
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return db_payment


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список платежей текущего пользователя
    """
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    payments = result.scalars().all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о конкретном платеже
    """
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this payment"
        )
    
    return payment
