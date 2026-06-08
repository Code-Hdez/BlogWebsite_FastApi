from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional, List, Union, Literal, Annotated
from fastapi import Form


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None
    image_url: Optional[str] = None
    # content: Optional[str] = "Se debe de rellenar este campo con el contenido"

    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str
    email: EmailStr

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
    # author: Optional[Author] = None

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
        tags: Annotated[Optional[List[str]], Form()] = None,
    ):
        tag_objs = [Tag(name=t) for t in (tags or [])]
        return cls(title=title, content=content, tag=tag_objs)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int
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
