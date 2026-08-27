from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, UTC
from microscope_backend.config import settings
from fastapi.security import OAuth2PasswordBearer

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