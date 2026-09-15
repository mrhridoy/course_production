import enum
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CourseLevel(str, enum.Enum):
    BEGINNER     = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED     = "advanced"


def _level_values(obj):
    return [e.value for e in obj]


class Course(Base):
    __tablename__ = "courses"

    id               = Column(Integer, primary_key=True, index=True)
    title            = Column(String(255), nullable=False)
    slug             = Column(String(300), unique=True, nullable=False)
    description      = Column(Text, nullable=True)
    thumbnail_url    = Column(String(500), nullable=True)
    promo_video_url  = Column(String(500), nullable=True)
    price            = Column(Float, default=0.0, nullable=False)
    duration_hours   = Column(Float, nullable=True)
    level            = Column(
        Enum(CourseLevel, values_callable=_level_values, name="courselevel"),
        default=CourseLevel.BEGINNER,
        nullable=False,
    )
    is_published     = Column(Boolean, default=False, nullable=False, index=True)
    category_id      = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    teacher_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at       = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category    = relationship("Category", back_populates="courses")
    teacher     = relationship("User", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    payments    = relationship("Payment", back_populates="course", cascade="all, delete-orphan")
