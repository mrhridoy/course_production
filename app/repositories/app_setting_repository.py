from typing import Optional
from sqlalchemy.orm import Session
from app.models.app_setting import AppSetting


class AppSettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> Optional[str]:
        row = self.db.query(AppSetting).filter(AppSetting.key == key).first()
        return row.value if row else None

    def set(self, key: str, value: Optional[str]) -> AppSetting:
        row = self.db.query(AppSetting).filter(AppSetting.key == key).first()
        if row is None:
            row = AppSetting(key=key, value=value)
            self.db.add(row)
        else:
            row.value = value
        self.db.commit()
        self.db.refresh(row)
        return row

    def all_keys(self, keys: list[str]) -> dict[str, Optional[str]]:
        rows = self.db.query(AppSetting).filter(AppSetting.key.in_(keys)).all()
        return {r.key: r.value for r in rows}
