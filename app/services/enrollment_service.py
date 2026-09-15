from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.enrollment_repository import EnrollmentRepository
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate


class EnrollmentService:
    def __init__(self, db: Session):
        self.repo = EnrollmentRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Enrollment]:
        return self.repo.get_all(skip, limit)

    def get_my_enrollments(self, student_id: int) -> List[Enrollment]:
        return self.repo.get_by_student(student_id)

    def enroll(self, data: EnrollmentCreate, student: User) -> Enrollment:
        existing = self.repo.get_by_student_and_course(student.id, data.course_id)
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")

        enrollment = Enrollment(student_id=student.id, course_id=data.course_id)
        return self.repo.create(enrollment)

    def update_status(self, enrollment_id: int, data: EnrollmentUpdate) -> Enrollment:
        enrollment = self.repo.get_by_id(enrollment_id)
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        enrollment.status = data.status
        return self.repo.update(enrollment)

    def delete(self, enrollment_id: int) -> None:
        enrollment = self.repo.get_by_id(enrollment_id)
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        self.repo.delete(enrollment)