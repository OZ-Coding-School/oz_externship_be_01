import time

from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment, AnswerImage
from apps.users.models import User
from core.utils.s3_file_upload import S3Uploader

# View는 HTTP 처리, Serializer는 데이터 처리


class AnswerImageSerializer(serializers.ModelSerializer[AnswerImage]):
    """답변 이미지 정보를 위한 시리얼라이저"""

    class Meta:
        model = AnswerImage
        fields = ["id", "img_url"]


class AuthorSerializer(serializers.ModelSerializer[User]):
    # 작성자 정보를 위한 별도 시리얼라이저
    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url", "role"]


class AnswerCommentListSerializer(serializers.ModelSerializer[AnswerComment]):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = AnswerComment
        fields = ["id", "answer_id", "author", "content", "created_at", "updated_at"]


class AnswerListSerializer(serializers.ModelSerializer[Answer]):
    author = AuthorSerializer(read_only=True)
    comments = AnswerCommentListSerializer(many=True, read_only=True)
    img_url = AnswerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = [
            "id",
            "question_id",
            "author",
            "content",
            "is_adopted",
            "created_at",
            "updated_at",
            "img_url",
            "comments",
        ]


class AnswerCreateSerializer(serializers.ModelSerializer[Answer]):
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    image_urls = AnswerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ["content", "image_files", "image_urls"]

    def validate_content(self, value: str) -> str:
        # 마크다운 형식 지원, 빈 내용 방지
        if not value or not value.strip():
            raise serializers.ValidationError("답변 내용을 입력해주세요.")
        return value.strip()

    def create(self, validated_data: dict) -> Answer:
        # image_files 분리 (Answer 모델에는 없는 필드)
        image_files = validated_data.pop("image_files", [])

        # 답변 생성
        answer = Answer.objects.create(**validated_data)

        # 등록할 이미지가 있는 경우에만
        if image_files:
            self._upload_images_to_s3(answer, image_files)

        return answer

    def _upload_images_to_s3(self, answer: Answer, image_files: list) -> None:
        """S3에 이미지 업로드 및 DB 저장"""
        s3_uploader = S3Uploader()

        for index, image_file in enumerate(image_files, 1):
            # 직관적인 + 유일한 파일명 생성: question_ID_answer_ID_image_순번_타임스탬프.확장자
            file_extension = image_file.name.split(".")[-1] if "." in image_file.name else "jpg"
            timestamp = int(time.time() * 1000)
            filename = f"question_{answer.question.id}_answer_{answer.id}_image_{index}_{timestamp}.{file_extension}"
            s3_key = f"qna/answers/{filename}"

            # S3에 파일 업로드
            s3_url = s3_uploader.upload_file(image_file, s3_key)

            if s3_url:
                # 업로드 성공 시 DB에 URL 저장
                AnswerImage.objects.create(answer=answer, img_url=s3_url)
            else:
                # 업로드 실패 시 로그 또는 에러 처리
                # 추후에 더 디테일하게 처리 예정
                pass


class AnswerUpdateSerializer(serializers.ModelSerializer[Answer]):
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    image_urls = AnswerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ["content", "image_files", "image_urls"]

    def validate_content(self, value: str) -> str:
        # 마크다운 형식 지원, 빈 내용 방지
        if not value or not value.strip():
            raise serializers.ValidationError("답변 내용을 입력해주세요.")
        return value.strip()

    def update(self, instance: Answer, validated_data: dict) -> Answer:
        # image_files 분리
        image_files = validated_data.pop("image_files", [])

        # 답변 내용 수정
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 새로 입력받은 이미지가 있는 경우에만
        if image_files:
            self._replace_images(instance, image_files)

        return instance

    def _replace_images(self, answer: Answer, image_files: list) -> None:
        """기존 이미지 삭제 후 새 이미지 업로드"""
        # 기존 이미지들의 S3 URL 수집 (삭제용)
        old_images = answer.images.all()
        old_s3_urls = [img.img_url for img in old_images]

        # DB에서 기존 이미지 레코드 삭제
        old_images.delete()

        # S3 업로드 클래스
        s3_uploader = S3Uploader()

        # 수정할 새 이미지들 업로드
        for index, image_file in enumerate(image_files, 1):
            # 직관적인 + 유일한 파일명 생성: question_ID_answer_ID_image_순번_타임스탬프.확장자
            file_extension = image_file.name.split(".")[-1] if "." in image_file.name else "jpg"
            timestamp = int(time.time() * 1000)
            filename = f"question_{answer.question.id}_answer_{answer.id}_image_{index}_{timestamp}.{file_extension}"
            s3_key = f"qna/answers/{filename}"

            # S3에 파일 업로드
            s3_url = s3_uploader.upload_file(image_file, s3_key)

            if s3_url:
                AnswerImage.objects.create(answer=answer, img_url=s3_url)
            else:
                # 업로드 실패 시 로그 또는 에러 처리
                # 추후에 더 디테일하게 처리 예정
                pass

        # 새 이미지 업로드 완료 후 기존 S3 파일들 삭제
        # (새 업로드가 성공한 후에 삭제하여 데이터 손실 방지)
        for old_url in old_s3_urls:
            s3_uploader.delete_file(old_url)


class AnswerCommentCreateSerializer(serializers.ModelSerializer[AnswerComment]):

    # TODO : 답변 id, 댓글 id(몇번째 댓글인지) 추가 예정
    class Meta:
        model = AnswerComment
        fields = ["content"]

    def validate_content(self, value: str) -> str:
        if len(value) > 500:
            raise serializers.ValidationError("댓글 내용은 500자 이하로 입력해야 합니다.")
        return value
