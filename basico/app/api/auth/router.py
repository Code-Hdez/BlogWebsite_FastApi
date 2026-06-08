import detect_installer
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from basico.app.api.auth.repository import UserRepository
from basico.app.core.db import get_db
from basico.app.models.user import UserOrm
from .schemas import RoleUpdate, TokenReponse, UserCreate, UserLogin, UserPublic
from app.core.security import (
    auth2_token,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    require_admin,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    if repository.get_by_email(payload.email):
        raise HTTPException(status_code=404, detail="Email ya registrado")

    user = repository.create(
        email=payload.email,
        hashsed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )

    db.commit()
    db.refresh(user)

    return UserPublic.model_validate(user)


@router.post("/login", response_model=TokenReponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):

    repository = UserRepository(db)
    user = repository.get_by_email(payload.email)

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas"
        )
    token = create_access_token(sub=str(user.id))

    return TokenReponse(access_token=token, user=UserPublic.model_validate(user))


@router.get("/me", response_model=UserPublic)
def read_me(current: UserOrm = Depends(get_current_user)):
    return UserPublic.model_validate(current)


@router.put("/role/{user_id}", response_model=UserPublic)
def set_role(
    user_id: int = Path(..., ge=1),
    payload: RoleUpdate = None,
    db: Session = Depends(get_db),
    _admin: UserOrm = Depends(require_admin),
):
    repository = UserRepository(db)
    user = repository.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    updated = repository.set_role(user, payload.role)

    db.commit()
    db.refresh(user)

    return UserPublic.model_validate(updated)


@router.post("/token")
async def token_endpoint(responde=Depends(auth2_token)):
    return responde
