import boto3
import io
import urllib.parse
from PIL import Image

s3 = boto3.client("s3")

# サムネイルのサイズ
THUMBNAIL_SIZE = (300, 300)


def lambda_handler(event, context):

    print("Lambda started")
    print(event)

    # S3イベントから情報を取得
    for record in event["Records"]:

        # バケット名
        bucket = record["s3"]["bucket"]["name"]

        # オブジェクトキー
        key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        print(f"Bucket: {bucket}")
        print(f"Key: {key}")

        # thumbnail.jpg が再度Lambdaを起動するのを防ぐ
        if "thumbnail.jpg" in key:
            print("Thumbnail file detected. Skip.")
            continue

        # original画像以外は処理しない
        if not key.endswith((".jpg", ".jpeg", ".png")):
            print("Unsupported file type. Skip.")
            continue

        # --------------------------------------------------
        # S3から画像を取得
        # --------------------------------------------------

        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        image_data = response["Body"].read()

        print(f"Original image size: {len(image_data)} bytes")

        # --------------------------------------------------
        # Pillowで画像を開く
        # --------------------------------------------------

        image = Image.open(
            io.BytesIO(image_data)
        )

        print(f"Original dimensions: {image.size}")

        # --------------------------------------------------
        # RGBに変換
        # --------------------------------------------------

        if image.mode != "RGB":
            image = image.convert("RGB")

        # --------------------------------------------------
        # サムネイル生成
        # --------------------------------------------------

        image.thumbnail(THUMBNAIL_SIZE)

        print(f"Thumbnail dimensions: {image.size}")

        # --------------------------------------------------
        # メモリ上にJPEGとして保存
        # --------------------------------------------------

        thumbnail_buffer = io.BytesIO()

        image.save(
            thumbnail_buffer,
            format="JPEG",
            quality=85
        )

        thumbnail_buffer.seek(0)

        # --------------------------------------------------
        # 保存先を作成
        # --------------------------------------------------

        # 例:
        #
        # profile-images/user001/original.jpg
        #
        # ↓
        #
        # profile-images/user001/thumbnail.jpg

        directory = key.rsplit("/", 1)[0]

        thumbnail_key = (
            f"{directory}/thumbnail.jpg"
        )

        print(f"Thumbnail key: {thumbnail_key}")

        # --------------------------------------------------
        # S3へアップロード
        # --------------------------------------------------

        s3.put_object(
            Bucket=bucket,
            Key=thumbnail_key,
            Body=thumbnail_buffer,
            ContentType="image/jpeg"
        )

        print(
            f"Thumbnail successfully created: "
            f"s3://{bucket}/{thumbnail_key}"
        )

    return {
        "statusCode": 200,
        "body": "Thumbnail generation completed"
    }
