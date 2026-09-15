from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate, RoleAssign


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_by_id(user_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        return self.repo.update(user)

    def assign_role(self, user_id: int, data: RoleAssign) -> User:
        user = self.get_by_id(user_id)
        user.role = data.role
        return self.repo.update(user)

    def toggle_active(self, user_id: int) -> User:
        user = self.get_by_id(user_id)
        user.is_active = not user.is_active
        return self.repo.update(user)

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        self.repo.delete(user)