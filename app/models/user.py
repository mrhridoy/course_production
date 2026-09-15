import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN   = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


def _role_values(obj):
    return [e.value for e in obj]


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    full_name  = Column(String(150), nullable=False)
    email      = Column(String(255), unique=True, index=True, nullable=False)
    phone      = Column(String(20), nullable=True)
    password   = Column(String(255), nullable=False)
    role       = Column(
        Enum(UserRole, values_callable=_role_values, name="userrole"),
        default=UserRole.STUDENT,
        nullable=False,
        index=True,
    )
    avatar     = Column(String(500), nullable=True)
    is_active  = Column(Boolean, default=True, nullable=False)

    # Phase 0 additions — used by Phase 4 password-reset / lockout flows.
    email_verified         = Column(Boolean, default=False, nullable=False)
    failed_login_attempts  = Column(Integer, default=0, nullable=False)
    locked_until           = Column(DateTime(timezone=True), nullable=True)

    # `default` (client-side) AND `server_default` together mean inserts work
    # whether the column was created with a DB default (fresh schema) or added
    # later by the deploy doctor (live upgrade path). Otherwise SQLAlchemy
    # would emit `created_at=NULL` on the legacy column → 500 on register.
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    courses        = relationship("Course", back_populates="teacher")
    enrollments    = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    payments       = relationship("Payment", back_populates="student", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
