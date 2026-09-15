from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, UserRole
from app.schemas.user import UserRegister, UserLogin, TokenOut


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.tokens = RefreshTokenRepository(db)

    # --- Public API ---

    def register(self, data: UserRegister) -> TokenOut:
        if self.users.get_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            full_name=data.full_name,
            email=data.email,  # already lowercased by the schema
            phone=data.phone,
            password=hash_password(data.password),
            role=UserRole.STUDENT,
        )
        user = self.users.create(user)
        return self._build_token(user)

    def login(self, data: UserLogin) -> TokenOut:
        user = self.users.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")
        return self._build_token(user)

    def refresh(self, refresh_token: str) -> TokenOut:
        """Single-use refresh: presented token is revoked, a new one is issued."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        jti = payload.get("jti")
        sub = payload.get("sub")
        if not jti or not sub:
            raise HTTPException(status_code=401, detail="Malformed refresh token")

        row = self.tokens.get_active_by_jti(jti)
        if not row:
            raise HTTPException(status_code=401, detail="Refresh token revoked or expired")

        user = self.users.get_by_id(int(sub))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        # Rotate: revoke the row we just consumed before issuing a new pair.
        self.tokens.revoke(row)
        return self._build_token(user)

    def logout(self, refresh_token: str) -> None:
        """Best-effort: revoke the row matching the presented token's jti."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return  # silent — don't leak whether the token was valid
        jti = payload.get("jti")
        if not jti:
            return
        row = self.tokens.get_active_by_jti(jti)
        if row:
            self.tokens.revoke(row)

    # --- Internal helpers ---

    def _build_token(self, user: User) -> TokenOut:
        token_data = {"sub": str(user.id), "role": user.role.value}
        access = create_access_token(token_data)
        refresh, jti, expires_at = create_refresh_token(token_data)
        self.tokens.create(user_id=user.id, jti=jti, expires_at=expires_at)
        return TokenOut(access_token=access, refresh_token=refresh, user=user)
