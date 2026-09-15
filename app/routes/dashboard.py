from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_admin, require_teacher
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import AdminDashboard, TeacherDashboard

router = APIRouter()


@router.get("/", response_model=AdminDashboard)
def admin_dashboard(db: Session = Depends(get_db), _=Depends(require_admin)):
    return DashboardService(db).get_admin_dashboard()


@router.get("/teacher", response_model=TeacherDashboard)
def teacher_dashboard(db: Session = Depends(get_db), current_user=Depends(require_teacher)):
    return DashboardService(db).get_teacher_dashboard(current_user.id)