import io
from typing import Optional
import boto3

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from app.config import AWS_REGION, S3_BUCKET
from app.database import users_table
from app.services.auth import decode_access_token


router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)


# --------------------------------------------------
# AWS S3
# --------------------------------------------------

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)


# --------------------------------------------------
# Authentication
# --------------------------------------------------

security = HTTPBearer()


def get_current_user_id(
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

    return user_id


# --------------------------------------------------
# Upload profile image
# --------------------------------------------------

@router.post("/image")
async def upload_profile_image(
    image: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):

    # --------------------------------------------------
    # Check content type
    # --------------------------------------------------

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if image.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WebP images are allowed"
        )


    # --------------------------------------------------
    # Read image
    # --------------------------------------------------

    image_data = await image.read()


    # --------------------------------------------------
    # File size limit
    # 10 MB
    # --------------------------------------------------

    max_size = 10 * 1024 * 1024

    if len(image_data) > max_size:

        raise HTTPException(
            status_code=400,
            detail="Image size must be 10MB or less"
        )


    if len(image_data) == 0:

        raise HTTPException(
            status_code=400,
            detail="Image file is empty"
        )


    # --------------------------------------------------
    # Verify image using Pillow
    # --------------------------------------------------

    try:

        from PIL import Image

        test_image = Image.open(
            io.BytesIO(image_data)
        )

        test_image.verify()

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )


    # --------------------------------------------------
    # S3 key
    # --------------------------------------------------

    s3_key = (
        f"profile-images/"
        f"{user_id}/"
        f"original.jpg"
    )


    # --------------------------------------------------
    # Upload to S3
    # --------------------------------------------------

    try:

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=image_data,
            ContentType=image.content_type
        )

    except Exception as e:

        print(
            f"S3 upload error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to upload image"
        )


    # --------------------------------------------------
    # Save S3 key to DynamoDB
    # --------------------------------------------------

    try:

        users_table.update_item(
            Key={
                "user_id": user_id
            },
            UpdateExpression=(
                "SET profile_image = :image"
            ),
            ExpressionAttributeValues={
                ":image": s3_key
            }
        )

    except Exception as e:

        print(
            f"DynamoDB update error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Image uploaded but profile update failed"
        )


    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "message": "Profile image uploaded successfully",
        "user_id": user_id,
        "profile_image": s3_key
    }

# --------------------------------------------------
# Get profile image URL
# --------------------------------------------------

@router.get("/image-url/{user_id}")
def get_profile_image_url(
    user_id: str
):

    # --------------------------------------------------
    # Get user information from DynamoDB
    # --------------------------------------------------

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


    # --------------------------------------------------
    # Get profile image S3 key
    # --------------------------------------------------

    profile_image = user.get(
        "profile_image"
    )

    if not profile_image:

        return {
            "url": None
        }


    # --------------------------------------------------
    # Create thumbnail key
    # --------------------------------------------------

    thumbnail_key = profile_image.replace(
        "original.jpg",
        "thumbnail.jpg"
    )


    # --------------------------------------------------
    # Generate Presigned URL
    # --------------------------------------------------

    try:

        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": thumbnail_key
            },
            ExpiresIn=3600
        )

    except Exception as e:

        print(
            f"Presigned URL error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate image URL"
        )


    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "url": url
    }

    # --------------------------------------------------
# Update profile
# --------------------------------------------------

from pydantic import BaseModel

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    height: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    job: Optional[str] = None
    income: Optional[int] = None
    region: Optional[str] = None
    hobbies: Optional[str] = None


@router.put("")
async def update_profile(
    profile: ProfileUpdate,
    user_id: str = Depends(get_current_user_id)
):

    # --------------------------------------------------
    # 更新データ取得
    # --------------------------------------------------

    update_data = profile.model_dump(
        exclude_none=True
    )


    if not update_data:

        raise HTTPException(
            status_code=400,
            detail="更新する項目がありません"
        )


    # --------------------------------------------------
    # DynamoDB UpdateExpression作成
    # --------------------------------------------------

    update_parts = []

    expression_attribute_names = {}

    expression_attribute_values = {}


    for key, value in update_data.items():

        name_key = f"#{key}"

        value_key = f":{key}"


        update_parts.append(
            f"{name_key} = {value_key}"
        )


        expression_attribute_names[
            name_key
        ] = key


        expression_attribute_values[
            value_key
        ] = value


    update_expression = (
        "SET " +
        ", ".join(update_parts)
    )


    # --------------------------------------------------
    # DynamoDB更新
    # --------------------------------------------------

    try:

        users_table.update_item(

            Key={
                "user_id": user_id
            },

            UpdateExpression=
                update_expression,

            ExpressionAttributeNames=
                expression_attribute_names,

            ExpressionAttributeValues=
                expression_attribute_values

        )

    except Exception as e:

        print(
            f"DynamoDB profile update error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update profile"
        )


    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "message": "Profile updated successfully",
        "user_id": user_id,
        "updated": update_data
    }
