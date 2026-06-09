from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Literal, Annotated
from fastapi import Form

from app.api.auth.schemas import UserPublic
from app.api.categories.schemas import CategoryPublic


class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30)

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)
    user: Optional[UserPublic] = None
    image_url: Optional[str] = None
    category: Optional[CategoryPublic] = None

    model_config = ConfigDict(from_attributes=True)


class PostCreate(PostBase):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (minimo 3 y maximo 100 caracteres)",
        examples=["Ultima noticia del dia"],
    )
    content: Optional[str] = Field(
        default="Contenido del post",
        min_length=10,
        description="Contenido que describe el titulo del post",
        examples=["En dicha noticia vamos a tratar lo ocurrido hacer varios dias"],
    )
    tags: List[Tag] = Field(default_factory=list)
    category_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El titulo no puede contener la palabra: 'spam'")
        return value

    @classmethod
    def as_form(
        cls,
        title: Annotated[str, Form(min_length=3)],
        content: Annotated[str, Form(min_length=10)],
        category_id: Annotated[Optional[int], Form(ge=1)] = None,
        tags: Annotated[Optional[List[str]], Form()] = None,
    ):
        tag_objs = []
        for value in tags or []:
            tag_objs.extend(
                Tag(name=name.strip().lower())
                for name in value.split(",")
                if name.strip()
            )

        return cls(title=title, content=content, tags=tag_objs, category_id=category_id)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int
    slug: str
    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]
