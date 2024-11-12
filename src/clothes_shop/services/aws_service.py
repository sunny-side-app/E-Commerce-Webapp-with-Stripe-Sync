import hashlib
import logging
import os
import string
from pathlib import Path
from typing import Any

import boto3
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(os.path.join(os.path.dirname(BASE_DIR), ".env"))
logger = logging.getLogger(__name__)


class AWS_Service:
    def __init__(self):
        self.aws_access_key_ID = env("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = env("AWS_SECRET_ACCESS_KEY")
        self.bucket = env("AWS_S3_IMAGE_BUCKET")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_ID,
            aws_secret_access_key=self.aws_secret_key,
        )

    def hash_filename(self, file_name):
        hash_object = hashlib.sha256(file_name.encode())
        hashed_name = hash_object.hexdigest()
        return f"{hashed_name}{file_name[file_name.rfind('.'):]}"

    def is_valid_image_extension(self, file):
        valid_extensions = {".jpg", ".jpeg", ".png"}
        return any(file.name.lower().endswith(ext) for ext in valid_extensions)

    def upload_to_s3(self, file):
        hashed_name = self.hash_filename(file.name)
        object_name = f"uploads/{hashed_name}"

        if not self.is_valid_image_extension(file):
            logger.error(ValueError("アップロード画像はjpegかpngのみ"))
            raise ValueError("アップロード画像はjpegかpngのみ")
        try:
            self.s3_client.upload_fileobj(file, self.bucket, object_name)
            logger.info(f"Successfully uploaded {file.name} to {self.bucket}/{object_name}")
            s3_url = f"https://{self.bucket}.s3.amazonaws.com/{object_name}"
            return s3_url
        except Exception as e:
            logger.error(f"S3 Upload Error: {e}")
            return None
