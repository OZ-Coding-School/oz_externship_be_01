from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import Test, TestQuestion
from apps.tests.permissions import IsAdminOrStaff
from apps.tests.serializers.test_question_serializers import (
    TestListItemSerializer,
    TestQuestionBulkCreateSerializer,
    TestQuestionCreateResponseSerializer,
    TestQuestionCreateSerializer,
    TestQuestionSimpleSerializer,
    TestQuestionUpdateSerializer,
)
from apps.users.models import User


# 문제 생성
class TestQuestionCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["[Admin] Test - Question (쪽지시험문제 생성/조회/수정/삭제)"],
        description="어드민이 특정 쪽지시험에 문제를 출제합니다.",
        request=TestQuestionCreateSerializer,
        responses={
            201: OpenApiResponse(response=TestQuestionCreateSerializer, description="문제 생성 성공"),
            400: OpenApiResponse(description="요청 오류"),
        },
    )
    def post(self, request):
        serializer = TestQuestionCreateSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()
            return Response(TestQuestionCreateResponseSerializer(question).data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 문제 수정
class TestQuestionUpdateDeleteView(APIView):
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin] Test - Question (쪽지시험문제 생성/조회/수정/삭제)"],
        description="어드민이 기존 쪽지시험 문제를 수정합니다.",
        request=TestQuestionUpdateSerializer,
        responses={
            200: OpenApiResponse(response=TestQuestionUpdateSerializer, description="문제 수정 성공"),
            400: OpenApiResponse(description="요청 오류"),
        },
    )
    def patch(self, request: Request, question_id: int) -> Response:
        question = get_object_or_404(TestQuestion, id=question_id)

        serializer = TestQuestionUpdateSerializer(instance=question, data=request.data, partial=True)
        if serializer.is_valid():
            updated_question = serializer.save()
            return Response(
                {
                    "id": updated_question.id,
                    **serializer.data,
                    "updated_at": updated_question.updated_at.isoformat(),
                },
                status=status.HTTP_200_OK,
            )
        return Response({"detail": "요청 오류입니다.", **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # 문제 삭제
    @extend_schema(
        tags=["[Admin] Test - Question (쪽지시험문제 생성/조회/수정/삭제)"],
        description="어드민이 등록한 쪽지시험 문제를 삭제합니다.",
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            403: OpenApiResponse(description="이 작업을 수행할 권한이 없습니다."),
            404: OpenApiResponse(description="문제를 찾을 수 없음"),
        },
    )
    def delete(self, request: Request, question_id: int) -> Response:
        question = TestQuestion.objects.filter(id=question_id).first()

        if not question:
            return Response(
                {"detail": "문제를 찾을 수 없음"},
                status=status.HTTP_404_NOT_FOUND,
            )

        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TestQuestionBulkUpdateAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin] Test - Question (쪽지시험문제 생성/조회/수정/삭제)"],
        description="어드민이 쪽지시험 문제를 한번에 수정 할 수 있습니다.",
        request=TestQuestionBulkCreateSerializer(),
        responses={
            201: OpenApiResponse(response=TestQuestionSimpleSerializer(many=True), description="문제 생성 성공"),
            400: OpenApiResponse(description="요청 오류"),
        },
    )
    def post(self, request):
        serializer = TestQuestionBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        created_questions = serializer.create(serializer.validated_data)  # → bulk_create() 리턴값

        response_data = TestQuestionCreateResponseSerializer(created_questions, many=True).data

        return Response(response_data, status=status.HTTP_201_CREATED)
