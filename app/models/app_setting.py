from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class AppSetting(Base):
    """Simple key/value store for runtime-configurable platform settings.

    Used right now for SMTP credentials so an admin can configure email from
    the dashboard rather than redeploying. Values are plain strings — for
    secrets this is acceptable for a learning project on a single-tenant DB.
    For production, layer in encryption-at-rest (e.g. Fernet) on `value`.
    """

    __tablename__ = "app_settings"

    id         = Column(Integer, primary_key=True, index=True)
    key        = Column(String(100), unique=True, nullable=False, index=True)
    value      = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
