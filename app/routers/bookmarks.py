from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"]
)


# ==================================================
# DynamoDB
# ==================================================

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-northeast-1"
)

bookmarks_table = dynamodb.Table("Bookmarks")
users_table = dynamodb.Table("Users")
matches_table = dynamodb.Table("Matches")


# ==================================================
# ブックマーク登録
# ==================================================

@router.post("")
def create_bookmark(
    user_id: str,
    target_user_id: str
):

    # ----------------------------------------------
    # 自分自身をブックマークできないようにする
    # ----------------------------------------------

    if user_id == target_user_id:

        raise HTTPException(
            status_code=400,
            detail="You cannot bookmark yourself"
        )


    # ----------------------------------------------
    # 対象ユーザーが存在するか確認
    # ----------------------------------------------

    response = users_table.get_item(
        Key={
            "user_id": target_user_id
        }
    )

    if "Item" not in response:

        raise HTTPException(
            status_code=404,
            detail="Target user not found"
        )


    # ----------------------------------------------
    # すでにブックマークしているか確認
    # ----------------------------------------------

    existing = bookmarks_table.get_item(
        Key={
            "user_id": user_id,
            "target_user_id": target_user_id
        }
    )

    if "Item" in existing:

        return {
            "message": "Already bookmarked",
            "matched": False
        }


    # ----------------------------------------------
    # ブックマーク保存
    # ----------------------------------------------

    created_at = datetime.now(
        timezone.utc
    ).isoformat()


    bookmarks_table.put_item(
        Item={
            "user_id": user_id,
            "target_user_id": target_user_id,
            "created_at": created_at
        }
    )


    # ----------------------------------------------
    # 相手から自分へのブックマークを確認
    # ----------------------------------------------

    reverse = bookmarks_table.get_item(
        Key={
            "user_id": target_user_id,
            "target_user_id": user_id
        }
    )


    matched = False


    # ----------------------------------------------
    # 相互ブックマーク
    # ----------------------------------------------

    if "Item" in reverse:

        user1, user2 = sorted(
            [user_id, target_user_id]
        )

        match_id = f"{user1}_{user2}"


        # すでにMatchが存在するか確認

        existing_match = matches_table.get_item(
            Key={
                "match_id": match_id
            }
        )


        if "Item" not in existing_match:

            matches_table.put_item(
                Item={
                    "match_id": match_id,
                    "user1": user1,
                    "user2": user2,
                    "created_at": created_at
                }
            )


        matched = True


    # ----------------------------------------------
    # Response
    # ----------------------------------------------

    return {
        "message": "Bookmark added",
        "matched": matched
    }


# ==================================================
# ブックマーク一覧
# ==================================================

@router.get("")
def get_bookmarks(
    user_id: str
):

    response = bookmarks_table.query(
        KeyConditionExpression=Key(
            "user_id"
        ).eq(user_id)
    )


    bookmarks = response.get(
        "Items",
        []
    )


    results = []


    for bookmark in bookmarks:

        target_user_id = bookmark[
            "target_user_id"
        ]


        user_response = users_table.get_item(
            Key={
                "user_id": target_user_id
            }
        )


        user = user_response.get(
            "Item"
        )


        if user:

            results.append({
                "user_id": user.get(
                    "user_id"
                ),
                "name": user.get(
                    "name"
                ),
                "age": int(
                    user["age"]
                ) if "age" in user else None,
                "height": int(
                    user["height"]
                ) if "height" in user else None,
                "job": user.get(
                    "job"
                ),
                "income": int(
                    user["income"]
                ) if "income" in user else None,
                "region": user.get(
                    "region"
                ),
                "hobbies": user.get(
                    "hobbies",
                    []
                )
            })


    return {
        "count": len(results),
        "users": results
    }


# ==================================================
# ブックマーク削除
# ==================================================

@router.delete("/{target_user_id}")
def delete_bookmark(
    target_user_id: str,
    user_id: str
):

    response = bookmarks_table.get_item(
        Key={
            "user_id": user_id,
            "target_user_id": target_user_id
        }
    )


    if "Item" not in response:

        raise HTTPException(
            status_code=404,
            detail="Bookmark not found"
        )


    bookmarks_table.delete_item(
        Key={
            "user_id": user_id,
            "target_user_id": target_user_id
        }
    )


    return {
        "message": "Bookmark deleted"
    }
