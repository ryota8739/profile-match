import boto3

from app.config import (
    AWS_REGION,
    USERS_TABLE,
    MESSAGES_TABLE
)


dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)


users_table = dynamodb.Table(
    USERS_TABLE
)


messages_table = dynamodb.Table(
    MESSAGES_TABLE
)
