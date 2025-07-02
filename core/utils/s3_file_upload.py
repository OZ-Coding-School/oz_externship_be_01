# core/utils/s3_file_upload.py

from typing import IO, Optional, cast

import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile


# 파일업로드 공통 유틸 클래스, 프로젝트 내 여러 앱에서 재사용할 수 있도록 core에 정의
class S3Uploader:

    def __init__(self):
        aws_access_key_id = cast(str, settings.AWS_ACCESS_KEY_ID)
        aws_secret_access_key = cast(str, settings.AWS_SECRET_ACCESS_KEY)
        aws_region = cast(str, settings.AWS_REGION)

        self.bucket = cast(str, settings.AWS_STORAGE_BUCKET_NAME)
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region,
        )

    # 단일 파일 업로드 후 URL 반환. 실패 시 None 반환
    def upload_file(self, file_obj: UploadedFile, s3_key: str) -> Optional[str]:

        try:
            self.client.upload_fileobj(
                file_obj,
                self.bucket,
                s3_key,
                ExtraArgs={"ContentType": file_obj.content_type},
            )
            return f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

        except NoCredentialsError:
            return None
