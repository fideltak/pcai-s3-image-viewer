import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

S3_ENDPOINT = os.getenv("S3_ENDPOINT") or None
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY") or None
AWS_ACCESS_KEY_SECRET = os.getenv("AWS_ACCESS_KEY_SECRET") or None
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN") or None
S3_ADDRESSING_STYLE = os.getenv("S3_ADDRESSING_STYLE", "auto")
S3_SSL_VERIFY = os.getenv("S3_SSL_VERIFY", "true").lower() != "false"

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_ACCESS_KEY_SECRET,
    aws_session_token=AWS_SESSION_TOKEN,
    verify=S3_SSL_VERIFY,
    config=Config(
        signature_version="s3v4",
        s3={
            "addressing_style": S3_ADDRESSING_STYLE
        }
    )
)

app = FastAPI(title="S3 Image Viewer")


@app.get("/images/{bucket}/{object_key:path}")
def get_image(bucket: str, object_key: str):
    try:
        obj = s3.get_object(
            Bucket=bucket,
            Key=object_key,
        )

        content_type = obj.get(
            "ContentType",
            "application/octet-stream"
        )

        allowed_types = {
            "image/png",
            "image/jpeg",
            "image/webp",
            "image/gif",
        }

        if content_type not in allowed_types:
            obj["Body"].close()
            raise HTTPException(
                status_code=415,
                detail="Unsupported image type",
            )

        try:
            image_data = obj["Body"].read()
        finally:
            obj["Body"].close()

        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "private, max-age=300",
            },
        )

    except ClientError as e:
        code = e.response["Error"]["Code"]

        if code in ("NoSuchKey", "NoSuchBucket", "404"):
            raise HTTPException(404, "Image not found")

        if code in ("AccessDenied", "403"):
            raise HTTPException(403, "Access denied")

        raise HTTPException(502, "Object storage error")
