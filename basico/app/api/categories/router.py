from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.categories.repository import CategoryRepository
from app.core.db import get_db
from app.api.categories.schemas import CategoryCreate, CategoryUpdate, CategoryPublic

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryPublic])
def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    pass


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    pass


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(category_id: int, db: Session = Depends(get_db)):
    pass


@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    pass

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    pass