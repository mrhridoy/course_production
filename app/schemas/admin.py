from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SmtpSettingsIn(BaseModel):
    """Admin-supplied SMTP configuration. Password is write-only."""
    host: Optional[str] = Field(None, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, max_length=255)  # if None on PUT, kept as-is
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = Field(None, max_length=150)
    use_tls: Optional[bool] = True


class SmtpSettingsOut(BaseModel):
    """Returned to admin. `password_set` is True if a password is stored;
    the password itself is never serialized."""
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password_set: bool = False
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    use_tls: bool = True


class TestSmtpRequest(BaseModel):
    to: EmailStr


class TestSmtpResponse(BaseModel):
    ok: bool
    detail: str
