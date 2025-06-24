from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.tests.serializers import TestQuestionSerializer


@extend_schema(
    request=TestQuestionSerializer,
    responses=TestQuestionSerializer,
    description="쪽지시험 문제를 등록합니다.",
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_test_questions(request: Request) -> Response:
    data = request.data
    required_fields = ["test_id", "content", "answer"]

    if not all(field in data for field in required_fields):
        return Response({"detail": "필수 항목이 누락되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "id": 5,
            "test_id": data["test_id"],
            "content": data["content"],
            "answer": data["answer"],
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    request=TestQuestionSerializer,
    responses=TestQuestionSerializer,
    description="쪽지시험 문제를 수정합니다.",
)
@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_test_questions(request: Request, question_id: int) -> Response:
    if question_id == 999:
        return Response({"detail": "테스트 질문을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data

    return Response(
        {
            "id": question_id,
            "content": data.get("content", "파이썬에서 리스트를 오름차순 정렬하는 함수는?"),
            "answer": data.get("answer", "sorted"),
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    description="쪽지시험 문제를 삭제합니다.",
    responses={
        204: None,
        403: {"description": "이 작업을 수행할 권한이 없습니다."},
        404: {"description": "쪽지시험 문제를 찾을 수 없습니다."},
    },
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_test_questions(request: Request, question_id: int) -> Response:
    if question_id == 999:
        return Response({"detail": "쪽지시험 문제를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    responses=TestQuestionSerializer(many=True),
    description="쪽지시험 문제 목록을 조회합니다.",
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_test_questions(request: Request) -> Response:
    return Response(
        [
            {"id": 1, "content": "파이썬에서 리스트를 정렬하는 함수는?", "answer": "sorted"},
            {"id": 2, "content": "파이썬의 반복문 키워드는?", "answer": "for"},
        ],
        status=status.HTTP_200_OK,
    )
