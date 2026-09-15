from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.user import User, UserRole


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        # Case-insensitive lookup so "Test@x.com" matches "test@x.com".
        return (
            self.db.query(User)
            .filter(User.email == (email or "").strip().lower())
            .first()
        )

    def get_by_role(self, role: UserRole) -> List[User]:
        return self.db.query(User).filter(User.role == role).all()

    def count_by_role(self, role: UserRole) -> int:
        return self.db.query(User).filter(User.role == role).count()
