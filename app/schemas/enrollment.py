from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enrollment import EnrollmentStatus


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentUpdate(BaseModel):
    status: EnrollmentStatus


class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    status: EnrollmentStatus
    # Optional: rows enrolled before Phase 0 have enrolled_at = NULL because
    # the DB column had no DEFAULT and server_default wasn't effective yet.
    enrolled_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True