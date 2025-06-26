from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status

from apps.qna.models import QuestionCategory, Question, Answer
from apps.qna.serializers.admin_serializers import (
    AdminCategoryCreateSerializer,
    AdminCategoryDeleteResponseSerializer,
    AdminAnswerDeleteSerializer,
    AdminQuestionDeleteSerializer,
)


# 질의응답 카테고리 등록
class AdminCategoryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["(Admin) 질문 카테고리 등록"]
    )
    def post(self, request):

        serializer = AdminCategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            return Response(data=serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 질의응답 카테고리 삭제
class AdminCategoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["(Admin) 질문 카테고리 삭제"]
    )
    def delete(self, request, category_id):
        serializer = AdminCategoryDeleteResponseSerializer(data=request.data)
        if serializer.is_valid():
            category = QuestionCategory.objects.get(id=category_id)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 답변 삭제
class AdminAnswerDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["(Admin) 답변 삭제"]
    )
    def delete(self, request, answer_id):
        serializer = AdminAnswerDeleteSerializer(data=request.data)
        if serializer.is_valid():
            answer = Answer.objects.get(id=answer_id)
            answer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 질문 삭제
class AdminQuestionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["(Admin) 질문 삭제"]
    )

    def delete(self, request, question_id):
        serializer = AdminQuestionDeleteSerializer(data=request.data)
        if serializer.is_valid():
            question = Question.objects.get(id=question_id)
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 질의응답 상세 조회
# 질문 목록 조회
# 징의응답 카테고리 목록 조회