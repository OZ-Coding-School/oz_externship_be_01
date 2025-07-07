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

    def delete_file(self, s3_url: str) -> bool:
        """S3 URL에서 파일 삭제"""
        try:
            # URL에서 S3 키 추출
            # https://bucket.s3.region.amazonaws.com/answers/filename.jpg -> answers/filename.jpg
            s3_key = s3_url.split(f"{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]

            self.client.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except Exception as e:
            return False

    # 기존 파일 위치에 새 파일을 덮어쓰고 동일 URL 반환. 실패 시 None 반환
    def update_file(self, file_obj: UploadedFile, s3_url: str) -> Optional[str]:

        try:
            # S3 URL에서 Key 추출
            s3_key = s3_url.split(f"{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            if not s3_key:
                return None

            # 기존 Key에 파일 덮어쓰기
            self.client.upload_fileobj(
                file_obj,
                self.bucket,
                s3_key,
                ExtraArgs={"ContentType": file_obj.content_type},
            )
            return s3_url  # Key는 같으니 기존 URL 반환
        except Exception as e:
            print(f"[ERROR] S3 update_file failed: {e}")
            return None
