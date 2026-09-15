from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentStatusUpdate, PaymentOut

router = APIRouter()


@router.get("/", response_model=List[PaymentOut])
def list_all_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_admin)):
    return PaymentService(db).get_all(skip, limit)


@router.get("/my", response_model=List[PaymentOut])
def my_payments(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return PaymentService(db).get_my_payments(current_user.id)


@router.post("/", response_model=PaymentOut, status_code=201)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return PaymentService(db).create(data, current_user)


@router.put("/{payment_id}/status", response_model=PaymentOut)
def update_payment_status(payment_id: int, data: PaymentStatusUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return PaymentService(db).update_status(payment_id, data)