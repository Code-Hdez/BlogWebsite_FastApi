from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from app.core.db import Base
from .associations import post_tags

if TYPE_CHECKING:
    from .author import AuthorORM
    from .tag import TagORM


class PostORM(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url = mapped_column(String(300), nullable=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Optional[AuthorORM]] = relationship(back_populates="posts")

    tags: Mapped[List[TagORM]] = relationship(
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",
        passive_deletes=True,
    )
