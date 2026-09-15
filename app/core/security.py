import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def utcnow() -> datetime:
    """Single source of UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "iat": utcnow(),
        "type": "access",
        "jti": uuid.uuid4().hex,
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> Tuple[str, str, datetime]:
    """Returns (token, jti, expires_at). Caller persists the jti so it's
    revocable on rotation/logout."""
    jti = uuid.uuid4().hex
    expires_at = utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        **data,
        "exp": expires_at,
        "iat": utcnow(),
        "type": "refresh",
        "jti": jti,
    }
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, expires_at


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# Password strength: min 8 chars, at least one letter and one digit. Pragmatic
# for a learning project — easy to extend later (zxcvbn etc.).
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


def password_is_strong(pw: str) -> bool:
    return bool(PASSWORD_RE.match(pw))
