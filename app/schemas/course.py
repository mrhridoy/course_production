from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.models.course import CourseLevel
from app.schemas.category import CategoryOut
from app.schemas.user import UserOut
from app.core.config import settings


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    promo_video_url: Optional[str] = None
    price: float = 0.0
    duration_hours: Optional[float] = None
    level: CourseLevel = CourseLevel.BEGINNER
    is_published: bool = False
    category_id: Optional[int] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    promo_video_url: Optional[str] = None
    price: Optional[float] = None
    duration_hours: Optional[float] = None
    level: Optional[CourseLevel] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None


class CourseOut(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    promo_video_url: Optional[str]
    price: float
    duration_hours: Optional[float]
    level: CourseLevel
    is_published: bool
    category: Optional[CategoryOut]
    teacher: Optional[UserOut]
    # Optional: courses created before Phase 0 may have created_at = NULL.
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("thumbnail_url", mode="before")
    @classmethod
    def build_thumbnail_url(cls, v):
        if v and not v.startswith("http"):
            return f"{settings.BASE_URL}{v}"
        return v

    class Config:
        from_attributes = True