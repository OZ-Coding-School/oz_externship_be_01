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
        request=AdminCategoryListSerializer,
    )
    def post(self, request: Request) -> Response:
        serializer = AdminCategoryListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
        serializer = AdminCategoryListSerializer(dummy.DUMMY_CATEGORY, many=True)
        resp_data = serializer.data
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
        if not any(q.id == category_id for q in dummy.DUMMY_CATEGORY):
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
        question = next((q for q in dummy.DUMMY_QUESTIONS if q.id == question_id), None)
        if not question:
            return Response({"detail": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 2. 카테고리
        category = question.category
        category_data = {
            "id": category.id,
            "name": category.name,
            "parent": category.parent.id if category.parent else None,
            "type": "parent" if category.parent is None else "child",
            "created_at": category.created_at,
            "updated_at": category.updated_at,
        }

        # 3. 질문 이미지들
        images = [
            {
                "id": img.id,
                "img_url": img.img_url,
                "created_at": img.created_at,
                "updated_at": img.updated_at,
            }
            for img in dummy.DUMMY_QUESTION_IMAGES
            if getattr(img.question, "id", None) == question_id
        ]

        # 4. 답변들 (답변 이미지 + 댓글 포함)
        answers = []
        for answer in dummy.DUMMY_ANSWERS:
            if getattr(answer.question, "id", None) != question_id:
                continue

            # 답변 이미지 (id 포함)
            answer_images = [
                {
                    "id": img.id,
                    "img_url": img.img_url,
                    "created_at": img.created_at,
                    "updated_at": img.updated_at,
                }
                for img in dummy.DUMMY_ANSWER_IMAGES
                if img.answer.id == answer.id
            ]

            # 답변 댓글
            answer_comments = [
                {
                    "content": comment.content,
                    "author": comment.author.id if comment.author else None,
                    "created_at": comment.created_at,
                    "updated_at": comment.updated_at,
                }
                for comment in dummy.DUMMY_ANSWER_COMMENTS
                if comment.answer.id == answer.id
            ]

            answers.append(
                {
                    "id": answer.id,
                    "content": answer.content,
                    "author": answer.author.id if answer.author else None,
                    "is_adopted": answer.is_adopted,
                    "created_at": answer.created_at,
                    "images": answer_images,
                    "comments": answer_comments,
                }
            )

        # 5. 최종 응답
        data = {
            "id": question.id,
            "title": question.title,
            "content": question.content,
            "author": question.author.id if question.author else None,
            "view_count": question.view_count,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
            "category": category_data,
            "images": images,
            "answers": answers,
        }

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
