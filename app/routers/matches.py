import boto3

from fastapi import APIRouter
from boto3.dynamodb.conditions import Attr


router = APIRouter(
    prefix="/matches",
    tags=["matches"]
)


# ==================================================
# DynamoDB
# ==================================================

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-northeast-1"
)


matches_table = dynamodb.Table(
    "Matches"
)


users_table = dynamodb.Table(
    "Users"
)


# ==================================================
# マッチ一覧
# ==================================================

@router.get("")
def get_matches(
    user_id: str
):

    # ----------------------------------------------
    # 自分がuser1またはuser2になっているMatchを取得
    # ----------------------------------------------

    response = matches_table.scan(
        FilterExpression=(
            Attr("user1").eq(user_id)
            | Attr("user2").eq(user_id)
        )
    )


    matches = response.get(
        "Items",
        []
    )


    results = []


    for match in matches:

        user1 = match["user1"]
        user2 = match["user2"]


        # 自分ではない方

        if user1 == user_id:

            target_user_id = user2

        else:

            target_user_id = user1


        response = users_table.get_item(
            Key={
                "user_id": target_user_id
            }
        )


        user = response.get(
            "Item"
        )


        if user:

            results.append({

                "match_id": match[
                    "match_id"
                ],

                "user_id": target_user_id,

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
        "matches": results
    }
