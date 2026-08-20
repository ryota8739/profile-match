from decimal import Decimal
from typing import Optional

import boto3
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


# --------------------------------------------------
# DynamoDB
# --------------------------------------------------

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-northeast-1"
)

users_table = dynamodb.Table("Users")


# --------------------------------------------------
# ユーザー情報を安全な形式に変換
# --------------------------------------------------

def user_response(user):
    return {
        "user_id": user.get("user_id"),
        "name": user.get("name"),
        "gender": user.get("gender"),
        "age": int(user["age"]) if "age" in user else None,
        "height": int(user["height"]) if "height" in user else None,
        "job": user.get("job"),
        "income": int(user["income"]) if "income" in user else None,
        "region": user.get("region"),
        "hobbies": user.get("hobbies", [])
    }


# --------------------------------------------------
# ユーザー検索
# --------------------------------------------------

@router.get("")
def search_users(
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_height: Optional[int] = None,
    max_height: Optional[int] = None,
    min_income: Optional[int] = None,
    max_income: Optional[int] = None,
    region: Optional[str] = None,
):
    response = users_table.scan()

    users = response.get("Items", [])

    results = []

    for user in users:

        # ------------------------------------------
        # 年齢
        # ------------------------------------------

        age = user.get("age")

        if age is not None:

            if min_age is not None:
                if age < Decimal(str(min_age)):
                    continue

            if max_age is not None:
                if age > Decimal(str(max_age)):
                    continue

        # ------------------------------------------
        # 身長
        # ------------------------------------------

        height = user.get("height")

        if height is not None:

            if min_height is not None:
                if height < Decimal(str(min_height)):
                    continue

            if max_height is not None:
                if height > Decimal(str(max_height)):
                    continue

        # ------------------------------------------
        # 年収
        # ------------------------------------------

        income = user.get("income")

        if income is not None:

            if min_income is not None:
                if income < Decimal(str(min_income)):
                    continue

            if max_income is not None:
                if income > Decimal(str(max_income)):
                    continue

        # ------------------------------------------
        # 地域
        # ------------------------------------------

        if region:

            if user.get("region") != region:
                continue

        # ------------------------------------------
        # レスポンス作成
        # ------------------------------------------

        results.append(
            user_response(user)
        )

    return {
        "count": len(results),
        "users": results
    }


# --------------------------------------------------
# ユーザー詳細
# --------------------------------------------------

@router.get("/{user_id}")
def get_user(user_id: str):

    response = users_table.get_item(
        Key={
            "user_id": user_id
        }
    )

    user = response.get("Item")

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user_response(user)
