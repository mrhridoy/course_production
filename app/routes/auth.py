from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenOut,
    UserOut,
    RefreshTokenRequest,
    LogoutRequest,
)

router = APIRouter()


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return AuthService(db).register(data)


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return AuthService(db).login(data)


@router.post("/refresh", response_model=TokenOut)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    AuthService(db).logout(data.refresh_token)
    return None


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user
