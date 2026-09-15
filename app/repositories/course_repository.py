from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.course import Course


class CourseRepository(BaseRepository[Course]):
    def __init__(self, db: Session):
        super().__init__(Course, db)

    def get_by_slug(self, slug: str) -> Optional[Course]:
        return self.db.query(Course).filter(Course.slug == slug).first()

    def get_by_teacher(self, teacher_id: int) -> List[Course]:
        return self.db.query(Course).filter(Course.teacher_id == teacher_id).all()

    def get_published(self, skip: int = 0, limit: int = 100) -> List[Course]:
        return self.db.query(Course).filter(Course.is_published == True).offset(skip).limit(limit).all()

    def count_by_teacher(self, teacher_id: int) -> int:
        return self.db.query(Course).filter(Course.teacher_id == teacher_id).count()

    def count_published(self) -> int:
        return self.db.query(Course).filter(Course.is_published == True).count()