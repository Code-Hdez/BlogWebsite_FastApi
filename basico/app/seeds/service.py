from contextlib import contextmanager
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models
from app.core.db import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.tag import TagORM
from app.models.user import UserORM
from app.models.category import CategoryORM
from app.seeds.data.categories import CATEGORIES
from app.seeds.data.tags import TAGS
from app.seeds.data.users import USERS


@contextmanager
def atomic(db: Session):
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise


def _user_by_email(db: Session, email: str) -> Optional[UserORM]:
    return db.execute(select(UserORM).where(UserORM.email == email)).scalars().first()


def _category_by_slug(db: Session, slug: str) -> Optional[CategoryORM]:
    return (
        db.execute(select(CategoryORM).where(CategoryORM.slug == slug))
        .scalars()
        .first()
    )


def _tag_by_name(db: Session, name: str) -> Optional[TagORM]:
    return db.execute(select(TagORM).where(TagORM.name == name)).scalars().first()


def seed_users(db: Session) -> None:
    with atomic(db):
        for data in USERS:
            obj = _user_by_email(db, data["email"])
            role = data.get("role", "user")
            if obj:
                changed = False
                if obj.full_name != data.get("full_name"):
                    obj.full_name = data.get("full_name")
                    changed = True
                if data.get("password"):
                    obj.hashed_password = hash_password(data["password"])
                    changed = True
                if obj.role != role:
                    obj.role = role
                    changed = True
                if changed:
                    db.add(obj)
            else:
                db.add(
                    UserORM(
                        email=data["email"],
                        full_name=data.get("full_name"),
                        role=role,
                        hashed_password=hash_password(data["password"]),
                    )
                )


def seed_categories(db: Session) -> None:
    with atomic(db):
        for data in CATEGORIES:
            obj = _category_by_slug(db, data["slug"])
            if obj:
                if obj.name != data["name"]:
                    obj.name = data["name"]
                    db.add(obj)
            else:
                db.add(CategoryORM(name=data["name"], slug=data["slug"]))


def seed_tags(db: Session) -> None:
    with atomic(db):
        for data in TAGS:
            obj = _tag_by_name(db, data["name"])
            if obj:
                if obj.name != data["name"]:
                    obj.name = data["name"]
                    db.add(obj)
            else:
                db.add(TagORM(name=data["name"]))


def create_schema() -> None:
    Base.metadata.create_all(bind=engine)


def run_all() -> None:
    create_schema()
    with SessionLocal() as db:
        seed_users(db)
        seed_categories(db)
        seed_tags(db)


def run_users() -> None:
    create_schema()
    with SessionLocal() as db:
        seed_users(db)


def run_tags() -> None:
    create_schema()
    with SessionLocal() as db:
        seed_tags(db)


def run_categories() -> None:
    create_schema()
    with SessionLocal() as db:
        seed_categories(db)
