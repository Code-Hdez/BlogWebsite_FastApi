from fastapi import (
    APIRouter,
    Query,
    Depends,
    Path,
    status,
    HTTPException,
    UploadFile,
    File,
)
from math import ceil
from typing import Optional, List, Union, Literal, Annotated
from app.core.db import get_db
from basico.app.api.auth import repository
from .schemas import PostPublic, PostCreate, PaginatedPost, PostUpdate, PostSummary
from .repository import PostRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.security import oauth2_scheme, get_current_user
from app.services.file_storage import save_upload_file
import time
import asyncio

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/sync")
def sync_endpoint():
    time.sleep(8)
    return {"meesage": "Funcion sincrona terminó"}


@router.get("/async")
async def async_endpoint():
    await asyncio.sleep(8)
    return {"meesage": "Funcion asincrona terminó"}


@router.get("", response_model=PaginatedPost)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="Parámetro obsoleto, usar query",
    ),
    query: Optional[str] = Query(
        default=None,
        description="Texto para buscar en los títulos de los posts",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚ-]+$",
    ),
    per_page: int = Query(10, ge=1, le=50, description="Numero de resultados (1-50)"),
    page: int = Query(1, ge=1, description="Número de página."),
    order_by: Literal["id", "title"] = Query("id", description="Campo de orden"),
    direction: Literal["asc", "desc"] = Query("asc", description="Dirección de orden."),
    db: Session = Depends(get_db),
):

    repository = PostRepository(db)
    query = query or text
    total, items = repository.search(query, order_by, direction, page, per_page)

    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = 2 if total_pages == 0 else min(page, total_pages)

    has_prev = current_page > 1
    has_next = current_page < total_pages

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items,
    )


@router.get("/by-tags", response_model=List[PostPublic])
def filters_by_tags(
    tags: List[str] = Query(..., min_length=2, description="Una o más etiquetas"),
    db: Session = Depends(get_db),
):
    repository = PostRepository(db)
    return repository.by_tags(tags)


@router.get(
    "/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post Encontrado",
)
def get_post(
    post_id: int = Path(
        ...,
        ge=1,
        title="ID del post",
        description="Identificador entero del post (debe de ser mayor a 1)",
        example=1,
    ),
    include_content: bool | None = Query(
        default=True,
        description="Booleano para indicar si se debe incluir el contenido del post en la respuesta",
    ),
    db: Session = Depends(get_db),
):

    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@router.post(
    "",
    response_model=PostPublic,
    response_description="Post creado (OK)",
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    post: Annotated[PostCreate, Depends(PostCreate.as_form)],
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repository = PostRepository(db)
    saved = None

    try:
        if image is not None:
            saved = save_upload_file(image)

        image_url = saved["url"] if saved else None

        post = repository.create_post(
            title=post.title,
            content=post.content,
            author=user,
            tags=[tag.model_dump() for tag in post.tags],
            image_url=image_url,
            category_id=post.category_id,
        )
        db.commit()
        db.refresh(post)
        return post

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El titulo ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")


@router.put(
    "/{posts_id}",
    response_model=PostPublic,
    response_description="Post actualizado",
    response_model_exclude_none=True,
)
def update_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    try:
        update = data.model_dump(exclude_unset=True)
        post = repository.update_post(post, update)
        db.commit()
        db.refresh(post)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el post")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    try:
        repository.delete_post(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el post")


@router.get("/secure")
def secure_endpoint(token: str = Depends(oauth2_scheme)):
    return {"message": "Acceso con token", "token_recibido": token}


@router.get("/post/{slug}", response_model=Union[PostPublic, PostSummary])
def get_post_by_slug(
    slug: str,
    include_content: bool | None = Query(
        default=True,
        description="Booleano para indicar si se debe incluir el contenido del post en la respuesta",
    ),
    db: Session = Depends(get_db),
):
    repository = PostRepository(db)
    post = repository.get_by_slug(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)
