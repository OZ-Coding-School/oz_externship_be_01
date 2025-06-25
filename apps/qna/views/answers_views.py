from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.models import Answer, Question
from apps.qna.serializers.answers_serializers import (
    AnswerCommentCreateSerializer,
    AnswerCreateSerializer,
    AnswerUpdateSerializer,
)


class AnswerCreateView(APIView):
    serializer_class = AnswerCreateSerializer

    def post(self, request: Request, question_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnswerUpdateView(APIView):
    serializer_class = AnswerUpdateSerializer

    def put(self, request: Request, answer_id: int) -> Response:
        answer = get_object_or_404(Answer, id=answer_id)
        serializer = self.serializer_class(instance=answer, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdoptAnswerView(APIView):
    def post(self, request: Request, question_id: int, answer_id: int) -> Response:
        return Response({"message": "OK"}, status=status.HTTP_200_OK)


class AnswerCommentCreateView(APIView):
    serializer_class = AnswerCommentCreateSerializer

    def post(self, request: Request, answer_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
