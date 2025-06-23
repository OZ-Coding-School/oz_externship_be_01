from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import TestDistribution

@api_view(["POST"])
def validate_join_code(request):
    exam_id = request.data.get("exam_id")
    join_code = request.data.get("join_code")

    if not exam_id or not join_code:
        return Response({"message": "exam_id와 join_code는 필수 입력값입니다."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        test = TestDistribution.objects.get(id=exam_id, join_code=join_code)
        return Response({
            "message": "참가코드가 유효합니다.",
            "exam_title": test.title  # 선택 사항
        }, status=status.HTTP_200_OK)
    except TestDistribution.DoesNotExist:
        return Response({"message": "잘못된 참가코드입니다."}, status=status.HTTP_400_BAD_REQUEST)
