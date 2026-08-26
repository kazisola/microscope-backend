from typing import Annotated
from fastapi import Depends, status, HTTPException
from microscope_backend.database import get_db
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from microscope_backend.models.user import User
from microscope_backend.core.auth import hash_password
from microscope_backend.schemas.user import UserCreate

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