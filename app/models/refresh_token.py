from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class RefreshToken(Base):
    """One row per issued refresh token. Lookup by `jti` (the JWT ID claim).

    Rotation: on /auth/refresh we mark the presented row revoked and insert a
    new one. Logout marks the current row revoked. Stolen tokens can be killed
    by revoking the row.
    """

    __tablename__ = "refresh_tokens"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    jti         = Column(String(64), unique=True, nullable=False, index=True)
    revoked     = Column(Boolean, default=False, nullable=False)
    expires_at  = Column(DateTime(timezone=True), nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at  = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")
