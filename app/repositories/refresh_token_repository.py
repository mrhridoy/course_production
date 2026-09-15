from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken
from app.core.security import utcnow


def _as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """SQLite drops tzinfo on roundtrip; treat naive datetimes as UTC."""
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, user_id: int, jti: str, expires_at: datetime) -> RefreshToken:
        row = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_active_by_jti(self, jti: str) -> Optional[RefreshToken]:
        row = self.db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
        if not row or row.revoked:
            return None
        expires = _as_utc(row.expires_at)
        if expires and expires < utcnow():
            return None
        return row

    def revoke(self, row: RefreshToken) -> None:
        row.revoked = True
        row.revoked_at = utcnow()
        self.db.commit()

    def revoke_all_for_user(self, user_id: int) -> int:
        q = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False)
        )
        n = q.update({"revoked": True, "revoked_at": utcnow()}, synchronize_session=False)
        self.db.commit()
        return n
