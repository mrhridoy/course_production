import re
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.repositories.course_repository import CourseRepository
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate
from app.utils.file_upload import save_thumbnail, delete_file


def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r"[\s_]+", "-", re.sub(r"[^\w\s-]", "", text))


class CourseService:
    def __init__(self, db: Session):
        self.repo = CourseRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Course]:
        return self.repo.get_all(skip, limit)

    def get_published(self, skip: int = 0, limit: int = 100) -> List[Course]:
        return self.repo.get_published(skip, limit)

    def get_by_id(self, course_id: int) -> Course:
        course = self.repo.get_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course

    def create(self, data: CourseCreate, teacher: User) -> Course:
        slug = slugify(data.title)
        existing = self.repo.get_by_slug(slug)
        if existing:
            slug = f"{slug}-{teacher.id}"

        course = Course(
            **data.model_dump(),
            slug=slug,
            teacher_id=teacher.id,
        )
        return self.repo.create(course)

    def update(self, course_id: int, data: CourseUpdate, current_user: User) -> Course:
        course = self.get_by_id(course_id)
        self._check_ownership(course, current_user)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(course, field, value)
        return self.repo.update(course)

    async def upload_thumbnail(self, course_id: int, file: UploadFile, current_user: User) -> Course:
        course = self.get_by_id(course_id)
        self._check_ownership(course, current_user)
        if course.thumbnail_url:
            delete_file(course.thumbnail_url)
        course.thumbnail_url = await save_thumbnail(file)
        return self.repo.update(course)

    def delete(self, course_id: int, current_user: User) -> None:
        course = self.get_by_id(course_id)
        self._check_ownership(course, current_user)
        if course.thumbnail_url:
            delete_file(course.thumbnail_url)
        self.repo.delete(course)

    def _check_ownership(self, course: Course, user: User):
        from app.models.user import UserRole
        if user.role != UserRole.ADMIN and course.teacher_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this course")