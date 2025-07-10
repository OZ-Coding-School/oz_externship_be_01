import time
import uuid

from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.serializers.images_serializers import (
    ImageFileDeleteSerializer,
    ImageFileUploadSerializer,
)
from core.utils.s3_file_upload import S3Uploader


class ImageUploadAPIView(APIView):
    serializer_class = ImageFileUploadSerializer
    parser_classes = [MultiPartParser]

    def __init__(self):
        super().__init__()
        self._s3uploader = None

    @property
    def s3uploader(self):
        """Lazy loading으로 S3Uploader 인스턴스 생성"""
        if self._s3uploader is None:
            self._s3uploader = S3Uploader()
        return self._s3uploader

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        s3_img_urls = []
        failed_images = []
        # Unique 한 이름으로 저장
        for img in serializer.validated_data.get("image_files", []):
            file_extension = img.name.split(".")[-1] if "." in img.name else "jpg"
            timestamp = int(time.time() * 1000)
            unique_id = str(uuid.uuid4())[:8]  # UUID의 앞 8자리만 사용
            filename = f"qna_image_{timestamp}_{unique_id}.{file_extension}"
            # TODO: 다른 기능 팀이랑 s3 파일 경로 컨벤션 상의 필요
            s3_key = f"qna/images/{filename}"
            # 저장 시도
            try:
                img_url = self.s3uploader.upload_file(img, s3_key)
                if img_url:  # 성공해서 url이 생기면
                    s3_img_urls.append(img_url)
                else:
                    failed_images.append(img.name)
            except:
                failed_images.append(img.name)

        # 실패한 파일이 있으면 업로드된 모든 파일 삭제
        if failed_images:
            # 업로드된 파일들 삭제
            for img_url in s3_img_urls:
                try:
                    self.s3uploader.delete_file(img_url)
                except Exception as e:
                    print(f"Error deleting {img_url}: {e}")

        response_data = {"upload_success": s3_img_urls, "upload_fail": failed_images}
        status = 400 if failed_images else 201

        return Response(response_data, status=status)


class ImageDeleteAPIView(APIView):
    serializer_class = ImageFileDeleteSerializer

    def __init__(self):
        super().__init__()
        self._s3uploader = None

    @property
    def s3delete(self):
        """Lazy loading으로 S3Uploader 인스턴스 생성"""
        if self._s3uploader is None:
            self._s3uploader = S3Uploader()
        return self._s3uploader

    def post(self, request):
        """클라이언트로부터 s3 업로드 된 이미지 URL 리스트를 받아서 S3에서 삭제"""
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        image_urls = serializer.validated_data.get("image_urls", [])

        deleted_images = []
        delete_fail = []

        # 삭제를 실패했을경우? 실패 에러 로그를 남긴다?
        for img_url in image_urls:
            try:
                image_delete_success = self.s3delete.delete_file(img_url)
                if image_delete_success:
                    deleted_images.append(img_url)
                else:
                    delete_fail.append(img_url)
            except Exception as e:
                delete_fail.append(img_url)

        response_data = {"delete_success": deleted_images, "delete_fail": delete_fail}
        status = 400 if delete_fail else 204

        return Response(response_data, status=status)
