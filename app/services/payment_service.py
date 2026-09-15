from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.payment_repository import PaymentRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.models.enrollment import Enrollment
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentStatusUpdate


class PaymentService:
    def __init__(self, db: Session):
        self.payment_repo = PaymentRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Payment]:
        return self.payment_repo.get_all(skip, limit)

    def get_my_payments(self, student_id: int) -> List[Payment]:
        return self.payment_repo.get_by_student(student_id)

    def create(self, data: PaymentCreate, student: User) -> Payment:
        enrollment = self.enrollment_repo.get_by_student_and_course(student.id, data.course_id)

        payment = Payment(
            student_id=student.id,
            course_id=data.course_id,
            enrollment_id=enrollment.id if enrollment else None,
            amount=data.amount,
            method=data.method,
            transaction_id=data.transaction_id,
            note=data.note,
            status=PaymentStatus.PENDING,
        )
        return self.payment_repo.create(payment)

    def update_status(self, payment_id: int, data: PaymentStatusUpdate) -> Payment:
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        payment.status = data.status
        if data.transaction_id:
            payment.transaction_id = data.transaction_id
        if data.note:
            payment.note = data.note
        if data.status == PaymentStatus.COMPLETED:
            payment.paid_at = datetime.now(timezone.utc)
            # Auto-enroll: create an Enrollment if one doesn't already exist
            existing = self.enrollment_repo.get_by_student_and_course(
                payment.student_id, payment.course_id
            )
            if not existing:
                enrollment = Enrollment(
                    student_id=payment.student_id,
                    course_id=payment.course_id,
                )
                enrollment = self.enrollment_repo.create(enrollment)
                payment.enrollment_id = enrollment.id

        return self.payment_repo.update(payment)