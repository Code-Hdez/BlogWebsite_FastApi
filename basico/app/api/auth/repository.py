from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from basico.app.core.db import get_db
from basico.app.models.user import UserOrm


class UserRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get(self, user_id: int) -> UserOrm | None:
        return self.db.get(UserOrm, user_id)

    def get_by_email(self, email: str) -> UserOrm | None:
        query = select(UserOrm).where(UserOrm.email == email)
        return self.db.execute(query).scalar_one_or_none

    def create(
        self, email: str, hashsed_password: str, full_name: str | None
    ) -> UserOrm:
        user = UserOrm(
            email=email, hashsed_password=hashsed_password, full_name=full_name
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def set_role(self, user: UserOrm, role: str) -> UserOrm:
        user.role = role

        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user
