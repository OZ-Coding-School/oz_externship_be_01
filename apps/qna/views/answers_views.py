from typing import cast

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.error_messages import AnswerErrorMessages, AnswerSuccessMessages
from apps.qna.models import Answer, AnswerComment, AnswerImage, Question
from apps.qna.permissions import IsStudentOrStaffOrAdminPermission, IsStudentPermission
from apps.qna.serializers.answers_serializers import (
    AnswerCommentCreateSerializer,
    AnswerCreateSerializer,
    AnswerListSerializer,
    AnswerUpdateSerializer,
)
from apps.users.models import User


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
        # 질문 정보 가져오기
        question = Question.objects.filter(pk=question_id).first()
        if not question:
            return Response(AnswerErrorMessages.QUESTION_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        # 요청 정보 가져오고 valid 확인
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Serializer에서 답변 생성 및 이미지 처리
        answer = serializer.save(question=question, author=user)

        # 응답 데이터 구성
        response_data = AnswerListSerializer(answer).data
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

        # 수정할 답변 가져오기
        question = Question.objects.filter(pk=question_id).first()
        if not question:
            return Response(AnswerErrorMessages.QUESTION_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        answer = Answer.objects.filter(pk=answer_id, question=question).first()
        if not answer:
            return Response(AnswerErrorMessages.ANSWER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        # 권한 확인: 본인이 작성한 답변만 수정 가능
        if answer.author != user:
            return Response(AnswerErrorMessages.ANSWER_AUTHOR_ONLY, status=status.HTTP_403_FORBIDDEN)

        # 요청 정보 가져오고 valid 확인
        serializer = self.serializer_class(answer, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Serializer에서 답변 수정 및 이미지 처리
        updated_answer = serializer.save()

        # 응답 데이터 구성
        response_data = AnswerListSerializer(updated_answer).data
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

        # 채택할 답변 가져오기
        question = Question.objects.filter(pk=question_id).first()
        if not question:
            return Response(AnswerErrorMessages.QUESTION_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        answer = Answer.objects.filter(pk=answer_id, question=question).first()
        if not answer:
            return Response(AnswerErrorMessages.ANSWER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        # 권한 확인 : 질문 작성자가 아닌 경우
        if question.author != user:
            return Response(AnswerErrorMessages.QUESTION_AUTHOR_ADOPT_ONLY, status=status.HTTP_403_FORBIDDEN)

        # 이미 채택된 답변이 존재하는 경우
        if question.answers.filter(is_adopted=True).exists():
            return Response(AnswerErrorMessages.ADOPTED_ANSWER_ALREADY_EXISTS, status=status.HTTP_400_BAD_REQUEST)

        # 이 답변이 이미 채택된 답변인경우
        if answer.is_adopted:
            return Response(AnswerErrorMessages.ANSWER_ALREADY_ADOPTED, status=status.HTTP_400_BAD_REQUEST)

        # 답변 채택
        answer.is_adopted = True
        answer.save()

        # 응답 데이터 구성
        return Response(AnswerSuccessMessages.ANSWER_ADOPTED, status=status.HTTP_200_OK)


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

        # 댓글 달 답변 가져오기
        answer = Answer.objects.filter(pk=answer_id).first()
        if not answer:
            return Response(AnswerErrorMessages.ANSWER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 댓글 생성
        comment = AnswerComment.objects.create(
            answer=answer,
            author=user,
            content=serializer.validated_data["content"],
        )

        # 응답 데이터 구성
        return Response(AnswerSuccessMessages.COMMENT_CREATED, status=status.HTTP_201_CREATED)
