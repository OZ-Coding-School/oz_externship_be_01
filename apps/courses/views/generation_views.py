from django.db.models.aggregates import Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.courses.models import Course, Generation
from apps.courses.serializers.generation_serializer import (
    GenerationCreateSerializer,
    GenerationDetailSerializer,
    GenerationListSerializer,
    GenerationTrendSerializer,
    MonthlyGenerationSerializer,
    OngoingSerializer,
)


# 기수 등록 API
class GenerationCreateView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationCreateSerializer

    def post(self, request:Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 기수 목록 API
class GenerationListView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationListSerializer

    def get(self, request:Request) -> Response:
        queryset = Generation.objects.select_related("course").annotate(registered_students=Count("students"))
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 기수 상세 정보 API
class GenerationDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationListSerializer

    def get(self, request:Request, pk:int) -> Response:
        try:
            gen = Generation.objects.select_related("course").annotate(registered_students=Count("students")).get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(gen)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerationUpdateView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationCreateSerializer

    def patch(self, request:Request, pk:int) -> Response    :
        try:
            gen = Generation.objects.get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(gen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(GenerationDetailSerializer(gen).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerationDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self,request:Request, pk:int) -> Response:
        try:
            gen = Generation.objects.annotate(registered_students=Coalesce(Count("students"),0)).get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not gen.registered_students == 0 or None:
            return Response({"이미 등록된 학생이 있어 삭제할 수 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

        gen.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerationTrendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationTrendSerializer

    def get(
        self,
        request:Request,
    )->Response:
        payload = {"course_id": 101, "course_name": "백엔드", "labels": [1, 2, 3, 4], "people_count": [25, 30, 28, 32]}
        serializer = self.serializer_class(data=payload)
        if serializer.is_valid(raise_exception=True):
            return  Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlygenerationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = MonthlyGenerationSerializer

    def get(self, request:Request) -> Response:
        payload = {
            "course_id": 101,
            "course_name": "백엔드",
            "labels": ["2025-1", "2025-2", "2025-3"],
            "people_count": [25, 30, 30],
        }

        serializer = self.serializer_class(data=payload)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_200_OK)


class OngoingGenerationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OngoingSerializer

    def get(self, request:Request) -> Response:
        payload = {"labels": ["백엔드", "프론트", "풀스택"], "people_count": [25, 30, 30]}
        serializer = self.serializer_class(data=payload)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_200_OK)
