from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class CategoryORM(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)

    posts: Mapped[list["PostORM"]] = relationship(
        "PostORM",
        back_populates="category",
        passive_deletes=True,
    )
