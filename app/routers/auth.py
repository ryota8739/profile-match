import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.database import users_table
from app.models.user import RegisterRequest
from app.services.auth import hash_password


router = APIRouter(
    tags=["auth"]
    )
@router.post("/register")
def register(
    user: RegisterRequest
):

    response = users_table.query(
        IndexName="email-index",
        KeyConditionExpression="email = :email",
        ExpressionAttributeValues={
            ":email": user.email
        }
    )

    if response["Items"]:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user_id = str(uuid.uuid4())

    item = {
        "user_id": user_id,
        "name": user.name,
        "email": user.email,
        "password_hash": hash_password(
            user.password
        ),
        "age": user.age,
        "gender": user.gender,
        "height": user.height,
        "job": user.job,
        "income": user.income,
        "region": user.region,
        "hobbies": user.hobbies,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    users_table.put_item(
        Item=item
    )

    return {
        "message": "User registered successfully",
        "user_id": user_id
    }
from app.models.user import LoginRequest
from app.services.auth import (
    verify_password,
    create_access_token
)
@router.post("/login")
def login(
    user: LoginRequest
):

    response = users_table.query(
        IndexName="email-index",
        KeyConditionExpression="email = :email",
        ExpressionAttributeValues={
            ":email": user.email
        }
    )

    items = response["Items"]

    if not items:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    db_user = items[0]

    if not verify_password(
        user.password,
        db_user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        db_user["user_id"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
        }
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth import decode_access_token
security = HTTPBearer()
@router.get("/me")
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    token = credentials.credentials

    try:
        user_id = decode_access_token(
            token
        )

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    response = users_table.get_item(
        Key={
            "user_id": user_id
        }
    )

    user = response.get("Item")

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.pop(
        "password_hash",
        None
    )

    return user
