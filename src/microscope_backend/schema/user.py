from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserBase(BaseModel):
    full_name: str = Field(min_length=5, max_length=50)
    username: str = Field(min_length=1, max_length=50)

class UserCreate(UserBase):
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=6)

class UserUpdate(UserBase):
    pass

class UserPublic(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

class UserPrivate(UserPublic):
    email: EmailStr = Field(max_length=100)