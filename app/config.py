import os

AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-northeast-1"
)

USERS_TABLE = os.getenv(
    "USERS_TABLE",
    "Users"
)

S3_BUCKET = os.getenv(
    "S3_BUCKET",
    "profile-match-app-20260819"
    )

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-secret-key"
)

MESSAGES_TABLE = os.getenv(
    "MESSAGES_TABLE",
    "Messages"
)

JWT_ALGORITHM = "HS256"
