import re
from typing import List

from django.conf import settings
from rest_framework import serializers

from apps.qna.models import Answer, AnswerImage


class ImageURLSerializer(serializers.ModelSerializer[AnswerImage]):
    """이미지 url 정보를 위한 시리얼라이저"""

    class Meta:
        model = AnswerImage
        fields = ["id", "img_url"]


class ImageFileUploadSerializer(serializers.Serializer):
    """이미지 파일을 요청으로 받을 때 사용하는 시리얼라이저"""

    image_files = serializers.ListField(child=serializers.ImageField(), required=False)


class ImageFileDeleteSerializer(serializers.Serializer):
    """이미지 url(s3 업로드 된 url)을 요청으로 받아서 삭제할 떄 사용하는 시리얼라이저"""

    image_urls = serializers.ListField(child=serializers.URLField())

    def validate_image_urls(self, value: List[str]) -> List[str]:
        """S3 URL 형식 검증"""
        if not value:
            raise serializers.ValidationError("삭제할 이미지 URL을 입력해주세요.")

        s3_bucket_domain = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com"

        for url in value:
            if not url.startswith(s3_bucket_domain):
                raise serializers.ValidationError(f"유효하지 않은 S3 URL입니다: {url}")

        return value


class ImageURLExtractFromMarkdown:
    """이미지 URL 추출을 위한 믹스인 클래스"""

    @staticmethod
    def _extract_image_urls_from_content(content: str) -> List[str]:
        """마크다운 content에서 이미지 URL 추출"""

        # 마크다운 이미지 패턴
        image_patterns = [
            r"!\[.*?\]\((https://[^)]+)\)",  # ![alt](url)
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # <img src="url">
        ]

        image_urls: List[str] = []
        for pattern in image_patterns:
            matches = re.findall(pattern, content)
            image_urls.extend(matches)

        # S3 URL만 필터링
        s3_bucket_domain = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com"
        valid_urls = [url for url in image_urls if url.startswith(s3_bucket_domain)]

        return valid_urls


class AnswerImageMixin(ImageURLExtractFromMarkdown):
    """답변 이미지 URL 저장을 위한 믹스인 클래스"""

    @staticmethod
    def _save_answer_images(answer: Answer, image_urls: List[str]) -> None:
        """AnswerImage 객체들을 생성하여 DB에 저장"""
        for img_url in image_urls:
            AnswerImage.objects.create(answer=answer, img_url=img_url)
