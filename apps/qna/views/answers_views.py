import time
from typing import cast

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.models import Answer, AnswerComment, AnswerImage, Question
from apps.qna.permissions import IsStudentOrStaffOrAdminPermission, IsStudentPermission
from apps.qna.serializers.answers_serializers import (
    AnswerCommentCreateSerializer,
    AnswerCreateSerializer,
    AnswerListSerializer,
    AnswerUpdateSerializer,
)
from apps.users.models import User
from core.utils.s3_file_upload import S3Uploader


class AnswerCreateView(APIView):
    serializer_class = AnswerCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrStaffOrAdminPermission]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=AnswerCreateSerializer,
        responses=AnswerListSerializer,
        description="질문에 대한 답변 생성",
        tags=["QNA-answer"],
    )
    def post(self, request: Request, question_id: int) -> Response:
        # IsAuthenticated permission으로 인해 request.user는 항상 User 타입
        user = cast(User, request.user)

        question = get_object_or_404(Question, pk=question_id)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 답변 생성
        answer = Answer.objects.create(question=question, author=user, content=serializer.validated_data.get("content"))

        # 이미지 파일 처리
        image_files = serializer.validated_data.get("image_files", [])
        answer_images = []

        # 등록할 이미지가 있는 경우에만
        if image_files:
            # S3 업로드 클래스
            s3_uploader = S3Uploader()

            for index, image_file in enumerate(image_files, 1):
                # 직관적인 + 유일한 파일명 생성: question_ID_answer_ID_image_순번_타임스탬프.확장자
                file_extension = image_file.name.split(".")[-1] if "." in image_file.name else "jpg"
                timestamp = int(time.time() * 1000)
                filename = f"question_{question.id}_answer_{answer.id}_image_{index}_{timestamp}.{file_extension}"
                s3_key = f"qna/answers/{filename}"

                # S3에 파일 업로드
                s3_url = s3_uploader.upload_file(image_file, s3_key)

                if s3_url:
                    # 업로드 성공 시 DB에 URL 저장
                    answer_image = AnswerImage.objects.create(answer=answer, img_url=s3_url)
                    answer_images.append(answer_image)
                else:
                    # 업로드 실패 시 로그 또는 에러 처리
                    # 추후에 더 디테일하게 처리 예정
                    pass

        # 응답 데이터 구성
        response_data = AnswerListSerializer(answer).data
        response_data["image_urls"] = [img.img_url for img in answer_images]
        return Response(response_data, status=status.HTTP_201_CREATED)


class AnswerUpdateView(APIView):
    serializer_class = AnswerUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrStaffOrAdminPermission]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=AnswerUpdateSerializer,
        responses=AnswerListSerializer,
        description="질문에 대한 답변 수정",
        tags=["QNA-answer"],
    )
    def put(self, request: Request, question_id: int, answer_id: int) -> Response:
        user = cast(User, request.user)

        question = get_object_or_404(Question, pk=question_id)
        answer = get_object_or_404(Answer, pk=answer_id, question=question)

        # 권한 확인: 본인이 작성한 답변만 수정 가능
        if answer.author != user:
            return Response({"detail": "본인이 작성한 답변만 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 답변 내용 수정
        answer.content = serializer.validated_data.get("content", answer.content)
        answer.save()

        image_files = serializer.validated_data.get("image_files", [])
        answer_images = []
        # 새로 입력받은 이미지가 있는 경우에만
        if image_files:
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
                filename = f"question_{question.id}_answer_{answer.id}_image_{index}_{timestamp}.{file_extension}"
                s3_key = f"qna/answers/{filename}"

                # S3에 파일 업로드
                s3_url = s3_uploader.upload_file(image_file, s3_key)

                if s3_url:
                    answer_image = AnswerImage.objects.create(answer=answer, img_url=s3_url)
                    answer_images.append(answer_image)
                else:
                    # 업로드 실패 시 로그 또는 에러 처리
                    # 추후에 더 디테일하게 처리 예정
                    pass

            # 새 이미지 업로드 완료 후 기존 S3 파일들 삭제
            # (새 업로드가 성공한 후에 삭제하여 데이터 손실 방지)
            for old_url in old_s3_urls:
                s3_uploader.delete_file(old_url)

        else:
            # 이미지 변경이 없는 경우 기존 이미지 유지
            answer_images = list(answer.images.all())

        # 응답 데이터 구성
        response_data = AnswerListSerializer(answer).data
        response_data["image_urls"] = [img.img_url for img in answer_images]
        return Response(response_data, status=status.HTTP_200_OK)


class AdoptAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudentPermission]

    @extend_schema(
        description="답변 채택",
        tags=["QNA-answer"],
        parameters=[
            OpenApiParameter(name="question_id", type=int, location=OpenApiParameter.PATH, description="질문 ID"),
            OpenApiParameter(name="answer_id", type=int, location=OpenApiParameter.PATH, description="채택할 답변 ID"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request: Request, question_id: int, answer_id: int) -> Response:
        user = cast(User, request.user)

        question = get_object_or_404(Question, pk=question_id)
        answer = get_object_or_404(Answer, pk=answer_id, question=question)

        # 권한 확인 : 질문 작성자가 아닌 경우
        if question.author != user:
            return Response({"detail": "본인의 질문에만 답변을 채택할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 이미 채택된 답변인경우
        if question.answers.filter(is_adopted=True).exists():
            return Response({"detail": "이미 채택된 답변이 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 답변 채택
        answer.is_adopted = True
        answer.save()

        # 응답 데이터 구성
        return Response({"detail": "답변 채택 완료"}, status=status.HTTP_200_OK)


class AnswerCommentCreateView(APIView):
    serializer_class = AnswerCommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrStaffOrAdminPermission]

    @extend_schema(
        request=AnswerCommentCreateSerializer,
        description="답변에 대한 댓글 생성",
        tags=["QNA-answer"],
    )
    def post(self, request: Request, answer_id: int) -> Response:
        user = cast(User, request.user)

        answer = get_object_or_404(Answer, pk=answer_id)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 댓글 생성
        comment = AnswerComment.objects.create(
            answer=answer,
            author=user,
            content=serializer.validated_data["content"],
        )

        # 응답 데이터 구성
        return Response({"detail": "댓글 등록 완료", "comment_id": comment.id}, status=status.HTTP_201_CREATED)
