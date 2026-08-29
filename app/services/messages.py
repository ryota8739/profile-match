import uuid

from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key

from app.database import messages_table


def create_message(
    match_id: str,
    sender_id: str,
    content: str
):

    message_id = str(
        uuid.uuid4()
    )

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    item = {
        "match_id": match_id,
        "created_at": created_at,
        "message_id": message_id,
        "sender_id": sender_id,
        "content": content
    }

    messages_table.put_item(
        Item=item
    )

    return item


def get_messages(
    match_id: str
):

    response = messages_table.query(
        KeyConditionExpression=
            Key("match_id").eq(match_id),

        ScanIndexForward=True
    )

    return response.get(
        "Items",
        []
    )
