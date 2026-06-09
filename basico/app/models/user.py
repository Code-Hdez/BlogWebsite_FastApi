from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.db import Base

Role = Literal["user", "editor", "admin"]


class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Role] = mapped_column(
        Enum("user", "editor", "admin", name="role_enum"), default="user"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    posts: Mapped[List["PostORM"]] = relationship(back_populates="user")
