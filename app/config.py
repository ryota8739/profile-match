import os

AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-northeast-1"
)

USERS_TABLE = os.getenv(
    "USERS_TABLE",
    "Users"
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-secret-key"
)

JWT_ALGORITHM = "HS256"
