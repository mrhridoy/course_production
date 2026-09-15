from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    course_id: int
    amount: float
    method: PaymentMethod
    transaction_id: Optional[str] = None
    note: Optional[str] = None


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus
    transaction_id: Optional[str] = None
    note: Optional[str] = None


class PaymentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrollment_id: Optional[int]
    amount: float
    currency: str
    method: PaymentMethod
    transaction_id: Optional[str]
    status: PaymentStatus
    note: Optional[str]
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True