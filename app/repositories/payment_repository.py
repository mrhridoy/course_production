from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base import BaseRepository
from app.models.payment import Payment, PaymentStatus


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session):
        super().__init__(Payment, db)

    def get_by_student(self, student_id: int) -> List[Payment]:
        return self.db.query(Payment).filter(Payment.student_id == student_id).all()

    def get_by_status(self, status: PaymentStatus) -> List[Payment]:
        return self.db.query(Payment).filter(Payment.status == status).all()

    def count_pending(self) -> int:
        return self.db.query(Payment).filter(Payment.status == PaymentStatus.PENDING).count()

    def total_revenue(self) -> float:
        result = self.db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).scalar()
        return result or 0.0

    def total_revenue_by_courses(self, course_ids: List[int]) -> float:
        result = self.db.query(func.sum(Payment.amount)).filter(
            Payment.course_id.in_(course_ids),
            Payment.status == PaymentStatus.COMPLETED,
        ).scalar()
        return result or 0.0