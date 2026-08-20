import io

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
