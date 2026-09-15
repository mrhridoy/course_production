from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import UserRole
from app.services.enrollment_service import EnrollmentService
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentOut

router = APIRouter()


@router.get("/", response_model=List[EnrollmentOut])
def list_all_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_admin)):
    return EnrollmentService(db).get_all(skip, limit)


@router.get("/my", response_model=List[EnrollmentOut])
def my_enrollments(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role == UserRole.ADMIN:
        return EnrollmentService(db).get_all()
    return EnrollmentService(db).get_my_enrollments(current_user.id)


@router.post("/", response_model=EnrollmentOut, status_code=201)
def enroll(data: EnrollmentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return EnrollmentService(db).enroll(data, current_user)


@router.put("/{enrollment_id}", response_model=EnrollmentOut)
def update_status(enrollment_id: int, data: EnrollmentUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return EnrollmentService(db).update_status(enrollment_id, data)


@router.delete("/{enrollment_id}", status_code=204)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    EnrollmentService(db).delete(enrollment_id)