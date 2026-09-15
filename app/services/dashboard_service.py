from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.payment_repository import PaymentRepository
from app.models.user import UserRole
from app.schemas.dashboard import AdminDashboard, TeacherDashboard


class DashboardService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.course_repo = CourseRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.payment_repo = PaymentRepository(db)

    def get_admin_dashboard(self) -> AdminDashboard:
        return AdminDashboard(
            total_users=self.user_repo.count(),
            total_students=self.user_repo.count_by_role(UserRole.STUDENT),
            total_teachers=self.user_repo.count_by_role(UserRole.TEACHER),
            total_courses=self.course_repo.count(),
            published_courses=self.course_repo.count_published(),
            total_enrollments=self.enrollment_repo.count(),
            total_revenue=self.payment_repo.total_revenue(),
            pending_payments=self.payment_repo.count_pending(),
        )

    def get_teacher_dashboard(self, teacher_id: int) -> TeacherDashboard:
        courses = self.course_repo.get_by_teacher(teacher_id)
        course_ids = [c.id for c in courses]
        published = sum(1 for c in courses if c.is_published)

        return TeacherDashboard(
            total_courses=len(courses),
            published_courses=published,
            total_enrollments=self.enrollment_repo.count_by_teacher_courses(course_ids),
            total_revenue=self.payment_repo.total_revenue_by_courses(course_ids),
        )