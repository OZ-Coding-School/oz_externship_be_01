from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import TestQuestion
from apps.tests.serializers.test_question_serializers import (
    DeleteResponseSerializer,
    TestListItemSerializer,
    TestQuestionCreateSerializer,
    TestQuestionUpdateSerializer,
)
from apps.tests.testquestion_permissions import IsAdminOrStaffByGroup


# 문제 생성
class TestQuestionCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["[Admin] Test - Question (쪽지시험문제 생성/조회/수정/삭제)"],
        description="Mock - 어드민이 특정 쪽지시험에 문제를 출제합니다.",
        request=TestQuestionCreateSerializer,
        responses={
            201: OpenApiResponse(response=TestQuestionCreateSerializer, description="문제 생성 성공"),
            400: OpenApiResponse(description="요청 오류"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = TestQuestionCreateSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {
                    **serializer.validated_data,
                    "id": 5,
                    "message": "테스트 질문이 성공적으로 생성되었습니다.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 목록 조회
class TestQuestionListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["[Admin] Test - Question (쪽지시험문제 생성/조회/수정/삭제)"],
        description="Mock - 수강생이 속한 기수에 배포된 쪽지시험 목록을 조회합니다.",
        responses={
            200: OpenApiResponse(response=TestListItemSerializer(many=True), description="시험 목록 조회 성공"),
            400: OpenApiResponse(description="기수 정보 누락 또는 요청 오류"),
        },
    )
    def get(self, request: Request) -> Response:
        status_param = request.query_params.get("status")

        mock_data = [
            {
                "test_id": 12,
                "test_title": "HTML/CSS 기초",
                "thumbnail_img_url": "https://example.com/image.png",
                "subject_title": "웹프로그래밍",
                "question_count": 10,
                "total_score": 100,
                "submission_status": "submitted",
                "score": 85,
                "correct_count": 8,
            },
            {
                "test_id": 13,
                "test_title": "JavaScript 문법 테스트",
                "thumbnail_img_url": "https://example.com/image2.png",
                "subject_title": "프론트엔드",
                "question_count": 12,
                "total_score": 120,
                "submission_status": "not_submitted",
            },
        ]

        return Response(mock_data, status=status.HTTP_200_OK)


# 문제 수정
class TestQuestionUpdateDeleteView(APIView):
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsAdminOrStaffByGroup]

    @extend_schema(
        tags=["[Admin] Test - Question (쪽지시험문제 생성/조회/수정/삭제)"],
        description="Mock - 어드민이 기존 쪽지시험 문제를 수정합니다.",
        request=TestQuestionUpdateSerializer,
        responses={
            200: OpenApiResponse(response=TestQuestionUpdateSerializer, description="문제 수정 성공"),
            400: OpenApiResponse(description="요청 오류"),
        },
    )
    def patch(self, request: Request, question_id: int) -> Response:
        serializer = TestQuestionUpdateSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            return Response(
                {"id": question_id, **serializer.validated_data, "updated_at": "2025-06-25T00:00:00Z"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 문제 삭제
    @extend_schema(
        tags=["[Admin] Test - Question (쪽지시험문제 생성/조회/수정/삭제)"],
        description="어드민이 등록한 쪽지시험 문제를 삭제합니다.",
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            403: OpenApiResponse(response=DeleteResponseSerializer, description="이 작업을 수행할 권한이 없습니다."),
            404: OpenApiResponse(response=DeleteResponseSerializer, description="문제를 찾을 수 없음"),
        },
    )
    def delete(self, request: Request, question_id: int) -> Response:
        question = get_object_or_404(TestQuestion, id=question_id)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
