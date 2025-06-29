from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.dummy import dummy
from apps.qna.serializers.admin_serializers import (
    AdminCategoryListSerializer,
    AdminQuestionDetailSerializer,
    AdminQuestionImageSerializer,
    AdminQuestionListSerializer,
)


# 카테고리 등록
class AdminCategoryCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["(Admin) QnA"],
        description="등록할 카테고리 ID",
        summary="카테고리 등록",
    )
    def post(self, request: Request, category_id: int) -> Response:
        serializer = AdminCategoryListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(category_id=category_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 카테고리 목록 조회
class AdminCategoryListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["(Admin) QnA"],
        description="조회할 카테고리 ID",
        summary="카테고리 목록 조회",
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AdminCategoryListSerializer(dummy.DUMMY_QUESTIONS, many=True)
        resp_data = serializer.data
        for data in resp_data:
            images = [image for image in dummy.DUMMY_QUESTION_IMAGES if data["id"] == image.question.id]
            data["images"] = AdminQuestionImageSerializer(images, many=True).data
        return Response(resp_data, status=status.HTTP_200_OK)


# 카테고리 삭제
class AdminCategoryDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["(Admin) QnA"],
        description="삭제할 카테고리 ID",
        summary="카테고리 삭제",
    )
    def delete(self, request: Request, category_id: int) -> Response:
        if not any(q.id == category_id for q in dummy.DUMMY_QUESTIONS):
            return Response({"detail": "해당 카테고리가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 원래는 이런 방식이 아닌데 더미라서 orm을 사용할 수 없기에 이렇게 합니다.
        dummy.DUMMY_CATEGORY = [q for q in dummy.DUMMY_CATEGORY if q.id != category_id]
        return Response(status=status.HTTP_204_NO_CONTENT)


# 질의응답 상세 조회
class AdminQnaDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["(Admin) QnA"], description="조회할 질의응답 ID", summary="질의응답 상세 조회")
    def get(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        # 1. 질문 찾기
        item = next((q for q in dummy.DUMMY_QUESTIONS if q.id == question_id), None)
        if not item:
            return Response({"detail": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 2. 직렬화
        serializer = AdminQuestionDetailSerializer(item)
        data = serializer.data

        # 3. 관련 이미지 mock 추가
        images = [
            img for img in dummy.DUMMY_QUESTION_IMAGES if getattr(img.question, "id", img.question) == question_id
        ]
        data["images"] = AdminQuestionImageSerializer(images, many=True).data

        return Response(data, status=status.HTTP_200_OK)


# 질문 목록 조회
class AdminQuestionListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["(Admin) QnA"], description="조회할 질문 ID", summary="질문 목록 조회")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AdminQuestionListSerializer(dummy.DUMMY_QUESTIONS, many=True)
        resp_data = serializer.data
        for data in resp_data:
            images = [image for image in dummy.DUMMY_QUESTION_IMAGES if data["id"] == image.question.id]
            data["images"] = AdminQuestionImageSerializer(images, many=True).data
        return Response(resp_data, status=status.HTTP_200_OK)


# 질문 삭제
class AdminQuestionDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["(Admin) QnA"], description="삭제할 질문 ID", summary="질문 삭제")
    def delete(self, request: Request, question_id: int) -> Response:
        if not any(q.id == question_id for q in dummy.DUMMY_QUESTIONS):
            return Response({"detail": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        # 원래는 이런 방식이 아닌데 더미라서 orm을 사용할 수 없기에 이렇게 합니다.
        dummy.DUMMY_QUESTIONS = [q for q in dummy.DUMMY_QUESTIONS if q.id != question_id]
        return Response(status=status.HTTP_204_NO_CONTENT)


# 답변 삭제
class AdminAnswerDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["(Admin) QnA"], description="삭제할 답변 ID", summary="답변 삭제")
    def delete(self, request: Request, answer_id: int) -> Response:
        if not any(q.id == answer_id for q in dummy.DUMMY_ANSWERS):
            return Response({"detail" "해당 답변이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        # 원래는 이런 방식이 아닌데 더미라서 orm을 사용할 수 없기에 이렇게 합니다.
        dummy.DUMMY_ANSWERS = [q for q in dummy.DUMMY_ANSWERS if q.id != answer_id]
        return Response(status=status.HTTP_204_NO_CONTENT)
