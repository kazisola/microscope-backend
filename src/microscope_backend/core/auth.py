from typing import Annotated
from fastapi import Depends, status, HTTPException
from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, UTC
from microscope_backend.config import settings
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from microscope_backend.database import get_db
from microscope_backend.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_mins
        )

    to_encode.update({"exp": expire})

    access_token = jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), settings.algorithm
    )

    return access_token


def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.algorithm],
        options={"require": ["sub", "exp"]}
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
    ) -> User:
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    result = await db.execute(
        select(User)
        .where(User.id == user_id_int)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found"
        )

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]