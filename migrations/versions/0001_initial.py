"""initial schema (consolidated)

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-08

This is the only migration. It builds the full schema for Phase 0:
- lowercase enum values (matches Python enum .value)
- unique (student_id, course_id) on enrollments
- cascade FKs on user / course deletes
- indexes on common filters
- refresh_tokens and app_settings tables
- email_verified, failed_login_attempts, locked_until on users
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- categories ----
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False, unique=True),
        sa.Column("slug", sa.String(200), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_categories_id", "categories", ["id"])

    # ---- users ----
    user_role = sa.Enum("admin", "teacher", "student", name="userrole")
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="student"),
        sa.Column("avatar", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    # ---- courses ----
    course_level = sa.Enum("beginner", "intermediate", "advanced", name="courselevel")
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(300), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
        sa.Column("promo_video_url", sa.String(500), nullable=True),
        sa.Column("price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("duration_hours", sa.Float(), nullable=True),
        sa.Column("level", course_level, nullable=False, server_default="beginner"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_courses_id", "courses", ["id"])
    op.create_index("ix_courses_is_published", "courses", ["is_published"])
    op.create_index("ix_courses_teacher_id", "courses", ["teacher_id"])

    # ---- enrollments ----
    enrollment_status = sa.Enum("active", "completed", "cancelled", name="enrollmentstatus")
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("status", enrollment_status, nullable=False, server_default="active"),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("student_id", "course_id", name="uq_enrollment_student_course"),
    )
    op.create_index("ix_enrollments_id", "enrollments", ["id"])
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"])

    # ---- payments ----
    payment_method = sa.Enum("bkash", "nagad", "card", "manual", name="paymentmethod")
    payment_status = sa.Enum("pending", "completed", "failed", "refunded", name="paymentstatus")
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("enrollment_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="BDT"),
        sa.Column("method", payment_method, nullable=False),
        sa.Column("transaction_id", sa.String(255), nullable=True, unique=True),
        sa.Column("status", payment_status, nullable=False, server_default="pending"),
        sa.Column("note", sa.String(500), nullable=True),
        sa.Column("refund_reason", sa.String(500), nullable=True),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["enrollment_id"], ["enrollments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_payments_id", "payments", ["id"])
    op.create_index("ix_payments_transaction_id", "payments", ["transaction_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_student_status", "payments", ["student_id", "status"])
    op.create_index("ix_payments_course_id", "payments", ["course_id"])

    # ---- refresh_tokens ----
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(64), nullable=False, unique=True),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"])
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"], unique=True)

    # ---- app_settings ----
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_app_settings_id", "app_settings", ["id"])
    op.create_index("ix_app_settings_key", "app_settings", ["key"], unique=True)


def downgrade() -> None:
    op.drop_table("app_settings")
    op.drop_table("refresh_tokens")
    op.drop_table("payments")
    op.drop_table("enrollments")
    op.drop_table("courses")
    op.drop_table("users")
    op.drop_table("categories")
    # Drop enum types (no-op on SQLite, real on Postgres)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for name in ("paymentstatus", "paymentmethod", "enrollmentstatus", "courselevel", "userrole"):
            sa.Enum(name=name).drop(bind, checkfirst=True)
