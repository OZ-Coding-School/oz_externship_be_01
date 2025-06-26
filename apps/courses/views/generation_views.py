from django.db.models.aggregates import Count
from h11 import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from apps.courses.models import Course, Generation
from apps.courses.serializers.generation_serializer import GenerationCreateSerializer, GenerationListSerializer, \
    GenerationDetailSerializer, GenerationTrendSerializer, MonthlyGenerationSerializer, OngoingSerializer


#기수 등록 API
class GenerationCreateView(APIView):
    serializer_class = GenerationCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#기수 목록 API
class GenerationListView(APIView):
    serializer_class = GenerationListSerializer

    def get(self, request):
        queryset = Generation.objects.select_related("course")\
            .annotate(registered_students=Count("students"))
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#기수 상세 정보 API
class GenerationDetailView(APIView):
    serializer_class = GenerationListSerializer

    def get(self, request, pk):
        try:
            gen=Generation.objects.select_related("course")\
                .annotate(registered_students=Count("students")).get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(gen)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GenerationUpdateView(APIView):
    serializer_class = GenerationCreateSerializer

    def patch(self, request, pk):
        try:
            gen=Generation.objects.get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(gen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(GenerationDetailSerializer(gen).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GenerationDeleteView(APIView):

    def delete(request, pk):
        try:
            gen=Generation.objects.annotate(registered_students=Count("students")).get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if gen.registered_students > 0:
            return Response({"이미 등록된 학생이 있어 삭제할 수 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

        gen.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GenerationTrendView(APIView):
    serializer_class = GenerationTrendSerializer

    def get(self, request,):
        payload = {
            'course_id' : 101 ,
            'course_name' : "백엔드",
            'labels' : [1,2,3,4] ,
            'data' : [25,30,28,32]
        }
        return Response(GenerationTrendSerializer(payload).data)

class MonthlygenerationView(APIView):
    serializer_class = MonthlyGenerationSerializer

    def get(self, request):
        payload = {
            'course_id' : 101 ,
            'course_name' : "백엔드",
            'labels' : ['2025-1','2025-2','2025-3'] ,
            'data' : [25,30,30]
        }

class OngoingGenerationView(APIView):
    serializer_class = OngoingSerializer

    def get(self, request):
        payload = {
            'labels' : ['백엔드','프론트','풀스택'],
            'data' : [25,30,30]
        }
        return Response(OngoingSerializer(payload).data)

