from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(150), unique=True, nullable=False)
    slug        = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), default=func.now(), server_default=func.now())

    # Relationships
    courses = relationship("Course", back_populates="category")