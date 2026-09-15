from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.services.settings_service import SettingsService
from app.schemas.admin import (
    SmtpSettingsIn,
    SmtpSettingsOut,
    TestSmtpRequest,
    TestSmtpResponse,
)

router = APIRouter()


@router.get("/smtp", response_model=SmtpSettingsOut)
def get_smtp(db: Session = Depends(get_db), _=Depends(require_admin)):
    return SettingsService(db).get_smtp()


@router.put("/smtp", response_model=SmtpSettingsOut)
def update_smtp(data: SmtpSettingsIn, db: Session = Depends(get_db), _=Depends(require_admin)):
    return SettingsService(db).update_smtp(data)


@router.post("/smtp/test", response_model=TestSmtpResponse)
def test_smtp(data: TestSmtpRequest, db: Session = Depends(get_db), _=Depends(require_admin)):
    ok, detail = SettingsService(db).send_test_email(str(data.to))
    return TestSmtpResponse(ok=ok, detail=detail)
