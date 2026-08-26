from fastapi import APIRouter, status
from microscope_backend.schemas.users import UserCreate, UserPrivate, Token


router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/hello")
async def hello():
    return {"message": "Hello!"}

@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def register_user(register_data: UserCreate):
    pass

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user():
    pass