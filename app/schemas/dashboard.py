from pydantic import BaseModel


class AdminDashboard(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_courses: int
    published_courses: int
    total_enrollments: int
    total_revenue: float
    pending_payments: int


class TeacherDashboard(BaseModel):
    total_courses: int
    published_courses: int
    total_enrollments: int
    total_revenue: float