from typing import Annotated
from fastapi import Depends, status, HTTPException
from microscope_backend.database import get_db
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from microscope_backend.models import User
from microscope_backend.core.auth import hash_password, verify_password, create_access_token, CurrentUser
from microscope_backend.schemas.user import UserCreate
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from microscope_backend.config import settings


async def register_user(
    register_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    result = await db.execute(
        select(User)
        .where(
            or_(
                func.lower(User.email) == register_data.email.lower(),
                func.lower(User.username) == register_data.username.lower()
            )
        )
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email/username already exists"
        )

    new_user = User(
        email=register_data.email,
        username=register_data.username,
        full_name=register_data.full_name,
        hashed_password=hash_password(register_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    result = await db.execute(
        select(User)
        .where(func.lower(User.email) == form_data.username.lower())
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User or password do not match",
            headers={"WWW-Authenticated": "Bearer"}
        )

    access_token_expires = timedelta(settings.access_token_expire_mins)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
        )

    return access_token


async def get_user_service(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user