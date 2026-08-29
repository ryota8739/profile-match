from pydantic import BaseModel, Field


class MessageCreate(BaseModel):

    match_id: str = Field(
        min_length=1
    )

    content: str = Field(
        min_length=1,
        max_length=1000
    )
