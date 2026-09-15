from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.enrollment import Enrollment, EnrollmentStatus


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self, db: Session):
        super().__init__(Enrollment, db)

    def get_by_student(self, student_id: int) -> List[Enrollment]:
        return self.db.query(Enrollment).filter(Enrollment.student_id == student_id).all()

    def get_by_course(self, course_id: int) -> List[Enrollment]:
        return self.db.query(Enrollment).filter(Enrollment.course_id == course_id).all()

    def get_by_student_and_course(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        return self.db.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
        ).first()

    def count_by_course(self, course_id: int) -> int:
        return self.db.query(Enrollment).filter(Enrollment.course_id == course_id).count()

    def count_by_teacher_courses(self, course_ids: List[int]) -> int:
        return self.db.query(Enrollment).filter(Enrollment.course_id.in_(course_ids)).count()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Enrollment]:
        return self.db.query(Enrollment).offset(skip).limit(limit).all()