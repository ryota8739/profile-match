from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from boto3.dynamodb.conditions import Key

from app.database import (
    messages_table,
    users_table
)

from app.models.message import MessageCreate

from app.services.auth import (
    get_current_user_id
)

from app.services.messages import (
    create_message,
    get_messages
)


router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)


# ==================================================
# Match確認
# ==================================================

def get_match(
    match_id: str
):

    from app.database import dynamodb

    matches_table = dynamodb.Table(
        "Matches"
    )

    response = matches_table.get_item(
        Key={
            "match_id": match_id
        }
    )

    return response.get(
        "Item"
    )


# ==================================================
# メッセージ取得
# ==================================================

@router.get("/{match_id}")
def get_message_list(

    match_id: str,

    current_user_id: str = Depends(
        get_current_user_id
    )
):

    match = get_match(
        match_id
    )

    if not match:

        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )


    # ----------------------------------------------
    # 自分がこのMatchの参加者か確認
    # ----------------------------------------------

    if (
        match["user1"] != current_user_id
        and
        match["user2"] != current_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )


    messages = get_messages(
        match_id
    )


    return {
        "match_id": match_id,
        "messages": messages
    }


# ==================================================
# メッセージ送信
# ==================================================

@router.post("")
def post_message(

    message: MessageCreate,

    current_user_id: str = Depends(
        get_current_user_id
    )

):

    match = get_match(
        message.match_id
    )

    if not match:

        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )


    # ----------------------------------------------
    # 自分がMatchの参加者か確認
    # ----------------------------------------------

    if (
        match["user1"] != current_user_id
        and
        match["user2"] != current_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )


    content = message.content.strip()


    if not content:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )


    created = create_message(

        match_id=message.match_id,

        sender_id=current_user_id,

        content=content

    )


    return created
