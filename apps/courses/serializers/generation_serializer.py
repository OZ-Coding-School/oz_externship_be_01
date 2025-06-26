from rest_framework import serializers
from datetime import date
from apps.courses.models import Generation, Course


#기수 등록
class GenerationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Generation
        fields = [
            "id",
            "course",
            'number',
            'max_student',
            'start_date',
            'end_date',
            'status',
        ]



        read_only_fields = ("id",)

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start > end:
            raise serializers.ValidationError("종료일은 시작일 이후여야 합니다.")

#기수 목록
class GenerationListSerializer(serializers.ModelSerializer):

    course_name = serializers.CharField(source="course.name", read_only=True)
    registered_students = serializers.IntegerField(read_only=True)

    class Meta:
        model = Generation
        fields = [
            'id',
            'course',
            'course_name',
            'number',
            'max_student',
            'registered_students',
            'start_date',
            'end_date',
            'status',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            "id",
            "course",
            "course_name",
            "registered_students",
            "created_at",
            "updated_at",
        ]

#기수 상세 조회
class GenerationDetailSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    course_tag = serializers.CharField(source="course.tag", read_only=True)
    course_description = serializers.CharField(source="course.description", read_only=True)
    registered_students = serializers.IntegerField(read_only=True)

    class Meta:
        model = Generation
        fields = [
            'id',
            'course',
            'course_name',
            'course_tag',
            'course_description',
            'number',
            'registered_students',
            'max_student',
            'start_date',
            'end_date',
            'status',
            'created_at',
            'updated_at',
        ]

        read_only_fields = fields

#기수 수정
class GenerationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Generation
        fields = [
            'start_date',
            'end_date',
        ]

    def validate(self, attrs):
        start = attrs.get("start_date",getattr(self.instance,"start_date",None))
        end = attrs.get("end_date",getattr(self.instance,"end_date",None))
        if start > end:
            raise serializers.ValidationError("종료일은 시작일 이후여야 합니다.")


#과정 - 기수 대시보드
class GenerationTrendSerializer(serializers.ModelSerializer):
    course_name = serializers.IntegerField(source="course.name", read_only=True)
    course_id = serializers.CharField(source="course.id", read_only=True)
    labels = serializers.ListField(child=serializers.IntegerField())
    data = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Generation
        fields = [
            'course_name',
            'course_id',
            'labels',
            'data',
        ]
        read_only_fields = fields

class MonthlyGenerationSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)
    labels = serializers.ListField(child=serializers.IntegerField())
    data = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Generation
        fields = [
            'course_id',
            'course_name',
            'labels',
            'data',
        ]
        read_only_fields = fields

class OngoingSerializer(serializers.ModelSerializer):
    labels = serializers.ListField(child=serializers.IntegerField())
    data = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Generation
        fields = [
            'labels',
            'data',
        ]