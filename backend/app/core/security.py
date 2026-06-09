import base64
import binascii
import hashlib
import hmac
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
from typing import Literal, Optional
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
import jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.api.auth.repository import UserRepository
from app.core.db import get_db
from app.models.user import UserORM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
PASSWORD_ALGORITHM = "sha256"
PASSWORD_ITERATIONS = 390_000

credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)


def raise_expire_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_forbidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos suficientes",
        headers={"WWW-Authenticate": "Bearer"},
    )


def invalid_credentials():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas",
    )


def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return jwt.encode(
        {"sub": sub, "exp": expire},
        key=settings.JWT_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    payload = jwt.decode(
        jwt=token, key=settings.JWT_KEY, algorithms=[settings.JWT_ALGORITHM]
    )

    return payload


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserORM:

    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub")

        if not sub:
            raise credentials_exc

        user_id = int(sub)

    except ExpiredSignatureError:
        raise raise_expire_token()
    except InvalidTokenError:
        raise credentials_exc
    except ValueError:
        raise credentials_exc
    except PyJWTError:
        raise invalid_credentials()

    user = db.get(UserORM, user_id)

    if not user or not user.is_active:
        raise invalid_credentials()

    return user


def _encode_bytes(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _decode_bytes(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(plain: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        PASSWORD_ALGORITHM,
        plain.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return (
        f"pbkdf2_{PASSWORD_ALGORITHM}"
        f"${PASSWORD_ITERATIONS}${_encode_bytes(salt)}${_encode_bytes(digest)}"
    )


def verify_password(plain: str, hashed: str) -> bool:
    try:
        method, iterations, salt, digest = hashed.split("$", 3)
        algorithm = method.removeprefix("pbkdf2_")
        if algorithm != PASSWORD_ALGORITHM:
            return False

        expected = hashlib.pbkdf2_hmac(
            algorithm,
            plain.encode("utf-8"),
            _decode_bytes(salt),
            int(iterations),
        )
        return hmac.compare_digest(_encode_bytes(expected), digest)
    except (binascii.Error, ValueError, TypeError):
        return False


def require_role(min_role: Literal["user", "editor", "admin"]):

    order = {"user": 0, "editor": 1, "admin": 2}

    def evaluation(user: UserORM = Depends(get_current_user)) -> UserORM:
        if order[user.role] < order[min_role]:
            raise raise_forbidden()
        return user

    return evaluation


async def auth2_token(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    repository = UserRepository(db)
    user = repository.get_by_email(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise invalid_credentials()

    token = create_access_token(sub=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")
