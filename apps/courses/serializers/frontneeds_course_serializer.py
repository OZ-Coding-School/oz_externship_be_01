from rest_framework import serializers

from apps.courses.models import Course


# --- CourseDropdownSerializer (새로 추가) ---
class CourseDropdownSerializer(serializers.ModelSerializer[Course]):
    """
    (Admin) 기수가 존재하는 과정 목록 조회 API를 위한 시리얼라이저.
    드롭다운 목록에 필요한 'id'와 'name' 필드만 포함합니다.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
        ]
        read_only_fields = fields
