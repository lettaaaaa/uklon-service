from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# User Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Driver Schemas
class DriverCreate(BaseModel):
    name: str
    phone: str
    license_number: str


class DriverResponse(BaseModel):
    id: int
    name: str
    phone: str
    license_number: str
    rating: float
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Car Schemas
class CarCreate(BaseModel):
    driver_id: int
    model: str
    plate_number: str
    color: Optional[str] = None
    year: Optional[int] = None


class CarResponse(BaseModel):
    id: int
    driver_id: int
    model: str
    plate_number: str
    color: Optional[str]
    year: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Ride Schemas
class RideCreate(BaseModel):
    pickup_location: str
    dropoff_location: str


class RideUpdate(BaseModel):
    driver_id: Optional[int] = None
    status: Optional[str] = None
    price: Optional[float] = None


class RideResponse(BaseModel):
    id: int
    user_id: int
    driver_id: Optional[int]
    pickup_location: str
    dropoff_location: str
    status: str
    price: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentCreate(BaseModel):
    ride_id: int
    amount: float
    payment_method: str


class PaymentResponse(BaseModel):
    id: int
    ride_id: int
    user_id: int
    amount: float
    payment_method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
