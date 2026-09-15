import enum
from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class EnrollmentStatus(str, enum.Enum):
    ACTIVE    = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def _status_values(obj):
    return [e.value for e in obj]


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_enrollment_student_course"),
    )

    id          = Column(Integer, primary_key=True, index=True)
    student_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id   = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    status      = Column(
        Enum(EnrollmentStatus, values_callable=_status_values, name="enrollmentstatus"),
        default=EnrollmentStatus.ACTIVE,
        nullable=False,
    )
    # `default` + `server_default`: works on both fresh schema and pre-Phase-0
    # live DB where the column was created without a DB-level DEFAULT.
    enrolled_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student  = relationship("User", back_populates="enrollments")
    course   = relationship("Course", back_populates="enrollments")
    payments = relationship("Payment", back_populates="enrollment")
