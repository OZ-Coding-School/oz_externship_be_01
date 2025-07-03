from rest_framework import serializers

from apps.courses.models import Generation


class GenerationDropdownSerializer(serializers.ModelSerializer[Generation]):
    """
    (Admin) 특정 과정의 기수 목록 조회 API를 위한 시리얼라이저.
    드롭다운 목록에 필요한 'id'와 'name' 필드만 포함합니다.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Generation
        fields = [
            "id",
            "name",
        ]
        read_only_fields = fields
