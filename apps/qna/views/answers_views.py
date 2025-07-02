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
from apps.qna.serializers.answers_serializers import (
    AnswerCommentCreateSerializer,
    AnswerCreateSerializer,
    AnswerListSerializer,
    AnswerUpdateSerializer,
)
from apps.users.models import User


class AnswerCreateView(APIView):
    serializer_class = AnswerCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=AnswerCreateSerializer,
        responses=AnswerListSerializer,
        description="질문에 대한 답변 생성",
        tags=["answer"],
    )
    def post(self, request: Request, question_id: int) -> Response:
        # IsAuthenticated permission으로 인해 request.user는 항상 User 타입
        user = cast(User, request.user)

        # 권한 확인: 수강생, 조교, 러닝 코치, 운영매니저, 어드민만 가능
        allowed_roles = [User.Role.STUDENT, User.Role.TA, User.Role.LC, User.Role.OM, User.Role.ADMIN]
        if user.role not in allowed_roles:
            return Response({"detail": "답변 작성 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        question = get_object_or_404(Question, pk=question_id)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 답변 생성
        answer = Answer.objects.create(
            question=question, author=request.user, content=serializer.validated_data.get("content")
        )

        # 이미지 파일 처리
        image_files = serializer.validated_data.get("image_files", [])
        answer_images = []

        for image_file in image_files:
            # 실제 파일 저장 로직 필요 (예: AWS S3, 로컬 파일 시스템)
            # 여기서는 간단히 파일명으로 URL 생성
            img_url = f"/media/answers/{answer.id}/{image_file.name}"
            answer_image = AnswerImage.objects.create(answer=answer, img_url=img_url)
            answer_images.append(answer_image)

        # 응답 데이터 구성
        response_data = AnswerListSerializer(answer).data
        response_data["image_urls"] = [img.img_url for img in answer_images]
        return Response(response_data, status=status.HTTP_201_CREATED)


class AnswerUpdateView(APIView):
    serializer_class = AnswerUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=AnswerUpdateSerializer,
        responses=AnswerListSerializer,
        description="질문에 대한 답변 수정",
        tags=["answer"],
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

        # 기존 이미지 삭제 후 새 이미지 업로드
        # 실제로는 기존 이미지 파일도 삭제해야 함
        answer.images.all().delete()

        image_files = serializer.validated_data.get("image_files", [])
        answer_images = []
        for image_file in image_files:
            img_url = f"/media/answers/{answer.id}/{image_file.name}"
            answer_image = AnswerImage.objects.create(answer=answer, img_url=img_url)
            answer_images.append(answer_image)

        # 응답 데이터 구성
        response_data = AnswerListSerializer(answer).data
        response_data["image_urls"] = [img.img_url for img in answer_images]
        return Response(response_data, status=status.HTTP_200_OK)


class AdoptAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="답변 채택",
        tags=["answer"],
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

        # 권한 확인: 수강생만 채택 가능
        if user.role != "STUDENT":
            return Response({"detail": "수강생만 답변을 채택할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 이미 채택된 답변인경우
        if question.answers.filter(is_adopted=True).exists():
            return Response({"message": "이미 채택된 답변이 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 답변 채택
        answer.is_adopted = True
        answer.save()

        # 응답 데이터 구성
        return Response({"message": "답변 채택 완료"}, status=status.HTTP_200_OK)


class AnswerCommentCreateView(APIView):
    serializer_class = AnswerCommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=AnswerCommentCreateSerializer,
        description="답변에 대한 댓글 생성",
        tags=["answer"],
    )
    def post(self, request: Request, answer_id: int) -> Response:
        user = cast(User, request.user)

        answer = get_object_or_404(Answer, pk=answer_id)

        # 권한 확인: 수강생, 조교, 러닝코치, 운영매니저, 관리자만 가능
        allowed_roles = [User.Role.STUDENT, User.Role.TA, User.Role.LC, User.Role.OM, User.Role.ADMIN]
        if user.role not in allowed_roles:
            return Response({"detail": "댓글 작성 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 댓글 생성
        comment = AnswerComment.objects.create(
            answer=answer,
            author=request.user,
            content=serializer.validated_data["content"],
        )

        # 응답 데이터 구성
        return Response({"message": "댓글 등록 완료", "comment_id": comment.id}, status=status.HTTP_201_CREATED)
