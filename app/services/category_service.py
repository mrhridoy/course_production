import re
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.category_repository import CategoryRepository
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r"[\s_]+", "-", re.sub(r"[^\w\s-]", "", text))


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def get_all(self) -> List[Category]:
        return self.repo.get_all(limit=500)

    def get_by_id(self, category_id: int) -> Category:
        cat = self.repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        return cat

    def create(self, data: CategoryCreate) -> Category:
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=400, detail="Category already exists")
        slug = slugify(data.name)
        cat = Category(name=data.name, slug=slug, description=data.description)
        return self.repo.create(cat)

    def update(self, category_id: int, data: CategoryUpdate) -> Category:
        cat = self.get_by_id(category_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(cat, field, value)
        if data.name:
            cat.slug = slugify(data.name)
        return self.repo.update(cat)

    def delete(self, category_id: int) -> None:
        cat = self.get_by_id(category_id)
        self.repo.delete(cat)