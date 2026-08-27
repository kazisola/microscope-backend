from typing import Annotated
from fastapi import APIRouter, status, Depends
from microscope_backend.schemas.user import UserCreate, UserPrivate, Token
from microscope_backend.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from microscope_backend.services import auth_service
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.post("/register", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    new_user = await auth_service.register_user(register_data, db)
    return new_user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    access_token = await auth_service.login_user(form_data, db)
    return Token(access_token=access_token, token_type="bearer")