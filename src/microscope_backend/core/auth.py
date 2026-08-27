from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, UTC
from microscope_backend.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

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