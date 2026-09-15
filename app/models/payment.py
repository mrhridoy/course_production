import enum
from sqlalchemy import Column, Integer, Float, String, Enum, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PaymentMethod(str, enum.Enum):
    BKASH  = "bkash"
    NAGAD  = "nagad"
    CARD   = "card"
    MANUAL = "manual"


class PaymentStatus(str, enum.Enum):
    PENDING   = "pending"
    COMPLETED = "completed"
    FAILED    = "failed"
    REFUNDED  = "refunded"


def _method_values(obj):
    return [e.value for e in obj]


def _status_values(obj):
    return [e.value for e in obj]


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_student_status", "student_id", "status"),
        Index("ix_payments_course_id", "course_id"),
    )

    id             = Column(Integer, primary_key=True, index=True)
    student_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id      = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrollment_id  = Column(Integer, ForeignKey("enrollments.id", ondelete="SET NULL"), nullable=True)
    amount         = Column(Float, nullable=False)
    currency       = Column(String(10), default="BDT", nullable=False)
    method         = Column(
        Enum(PaymentMethod, values_callable=_method_values, name="paymentmethod"),
        nullable=False,
    )
    transaction_id = Column(String(255), nullable=True, unique=True, index=True)
    status         = Column(
        Enum(PaymentStatus, values_callable=_status_values, name="paymentstatus"),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
    )
    note           = Column(String(500), nullable=True)

    # Refund tracking (Phase 2 will populate via state machine).
    refund_reason  = Column(String(500), nullable=True)
    refunded_at    = Column(DateTime(timezone=True), nullable=True)

    paid_at        = Column(DateTime(timezone=True), nullable=True)
    # `default` (Python-side) AND `server_default` together so inserts work
    # whether the column has a DB-level DEFAULT (fresh schema) or was created
    # without one (pre-Phase-0 live DB upgraded via deploy doctor).
    created_at     = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)

    # Relationships
    student    = relationship("User", back_populates="payments")
    course     = relationship("Course", back_populates="payments")
    enrollment = relationship("Enrollment", back_populates="payments")
