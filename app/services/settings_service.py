"""SMTP settings storage + email send helper.

Settings are stored as flat key/value pairs in the `app_settings` table:

    smtp.host          -> str
    smtp.port          -> str (cast to int)
    smtp.username      -> str
    smtp.password      -> str         (stored plaintext; learning-project trade-off)
    smtp.from_email    -> str
    smtp.from_name     -> str
    smtp.use_tls       -> "1"/"0"

The admin can write these via PUT /admin/settings, then trigger a test email
to verify deliverability before students rely on it (e.g. password reset).
"""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings as app_settings
from app.repositories.app_setting_repository import AppSettingRepository
from app.schemas.admin import SmtpSettingsIn, SmtpSettingsOut


SMTP_KEYS = [
    "smtp.host",
    "smtp.port",
    "smtp.username",
    "smtp.password",
    "smtp.from_email",
    "smtp.from_name",
    "smtp.use_tls",
]


def _to_bool(v: Optional[str], default: bool = True) -> bool:
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _to_int(v: Optional[str]) -> Optional[int]:
    try:
        return int(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


class SettingsService:
    def __init__(self, db: Session):
        self.repo = AppSettingRepository(db)

    # ----- SMTP -----

    def get_smtp(self) -> SmtpSettingsOut:
        kv = self.repo.all_keys(SMTP_KEYS)
        return SmtpSettingsOut(
            host=kv.get("smtp.host"),
            port=_to_int(kv.get("smtp.port")),
            username=kv.get("smtp.username"),
            password_set=bool(kv.get("smtp.password")),
            from_email=kv.get("smtp.from_email"),
            from_name=kv.get("smtp.from_name"),
            use_tls=_to_bool(kv.get("smtp.use_tls"), True),
        )

    def update_smtp(self, data: SmtpSettingsIn) -> SmtpSettingsOut:
        if data.host is not None:
            self.repo.set("smtp.host", data.host or None)
        if data.port is not None:
            self.repo.set("smtp.port", str(data.port))
        if data.username is not None:
            self.repo.set("smtp.username", data.username or None)
        if data.password is not None and data.password != "":
            # Empty string would be ambiguous; require an explicit value to change.
            self.repo.set("smtp.password", data.password)
        if data.from_email is not None:
            self.repo.set("smtp.from_email", str(data.from_email) if data.from_email else None)
        if data.from_name is not None:
            self.repo.set("smtp.from_name", data.from_name or None)
        if data.use_tls is not None:
            self.repo.set("smtp.use_tls", "1" if data.use_tls else "0")
        return self.get_smtp()

    # ----- Email send -----

    def _smtp_creds(self):
        kv = self.repo.all_keys(SMTP_KEYS)
        host = kv.get("smtp.host")
        port = _to_int(kv.get("smtp.port"))
        username = kv.get("smtp.username")
        password = kv.get("smtp.password")
        from_email = kv.get("smtp.from_email") or username
        from_name = kv.get("smtp.from_name") or "ICT Bangladesh"
        use_tls = _to_bool(kv.get("smtp.use_tls"), True)
        if not host or not port or not from_email:
            raise RuntimeError(
                "SMTP is not configured. Set host, port, and from_email via /admin/settings."
            )
        return host, port, username, password, from_email, from_name, use_tls

    def send_email(self, to: str, subject: str, body: str) -> None:
        """Synchronous send. Returns nothing on success; raises on failure.

        In TESTING mode this is a no-op so the test suite never hits the network.
        """
        if app_settings.TESTING:
            return

        host, port, username, password, from_email, from_name, use_tls = self._smtp_creds()
        msg = EmailMessage()
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        if use_tls:
            ctx = ssl.create_default_context()
            with smtplib.SMTP(host, port, timeout=15) as smtp:
                smtp.starttls(context=ctx)
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP_SSL(host, port, timeout=15) as smtp:
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(msg)

    def send_test_email(self, to: str) -> tuple[bool, str]:
        try:
            self.send_email(
                to=to,
                subject="ICT Bangladesh — SMTP test",
                body=(
                    "This is a test email from your ICT Bangladesh admin panel.\n\n"
                    "If you received this, SMTP is configured correctly."
                ),
            )
            return True, "Test email sent."
        except Exception as e:  # noqa: BLE001
            return False, f"SMTP error: {e}"
