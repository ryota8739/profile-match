import bcrypt
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)


def hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str
) -> bool:

    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hash_bytes
    )


def create_access_token(
    user_id: str
) -> str:

    expire = datetime.now(
        timezone.utc
    ) + timedelta(hours=24)

    payload = {
        "sub": user_id,
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(
    token: str
) -> str:

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM]
    )

    return payload["sub"]
