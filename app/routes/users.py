from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.services.user_service import UserService
from app.schemas.user import UserOut, UserUpdate, RoleAssign

router = APIRouter()


@router.get("/", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_admin)):
    return UserService(db).get_all(skip, limit)


@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    return UserService(db).get_by_id(user_id)


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return UserService(db).update(user_id, data)


@router.put("/{user_id}/role", response_model=UserOut)
def assign_role(user_id: int, data: RoleAssign, db: Session = Depends(get_db), _=Depends(require_admin)):
    return UserService(db).assign_role(user_id, data)


@router.patch("/{user_id}/toggle-active", response_model=UserOut)
def toggle_active(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    return UserService(db).toggle_active(user_id)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    UserService(db).delete(user_id)