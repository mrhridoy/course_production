"""Idempotent admin seeder.

Run after migrations to create the initial admin login. Usage:

    python scripts/seed_admin.py admin@example.com Passw0rd!

If the user already exists, role is upgraded to admin (no password change).
Useful right after a fresh DB so you can sign in and configure SMTP.
"""

from __future__ import annotations

import sys

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password, password_is_strong
from app.models.user import User, UserRole


def upsert_admin(db: Session, email: str, password: str, full_name: str = "Administrator") -> User:
    email = email.strip().lower()
    if not password_is_strong(password):
        raise SystemExit("Password must be 8+ chars and contain letters and digits.")

    user = db.query(User).filter(User.email == email).first()
    if user:
        user.role = UserRole.ADMIN
        user.is_active = True
        db.commit()
        db.refresh(user)
        print(f"Promoted existing user to admin: {email}")
        return user

    user = User(
        full_name=full_name,
        email=email,
        password=hash_password(password),
        role=UserRole.ADMIN,
        is_active=True,
        email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created admin user: {email}")
    return user


def main():
    if len(sys.argv) < 3:
        print("usage: python scripts/seed_admin.py <email> <password> [full_name]")
        raise SystemExit(2)

    email, password = sys.argv[1], sys.argv[2]
    full_name = sys.argv[3] if len(sys.argv) > 3 else "Administrator"

    db = SessionLocal()
    try:
        upsert_admin(db, email, password, full_name)
    finally:
        db.close()


if __name__ == "__main__":
    main()
