from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    methods=["DELETE"],
    description="관리자 또는 스태프가 등록한 쪽지시험 문제를 Hard Delete 방식으로 삭제합니다.",
    responses={
        204: None,
        403: {"세부 정보 : 이 작업을 수행할 권한이 없습니다."},
        404: {"세부 정보 : 테스트 질문을 찾을 수 없습니다."}
    }
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_test_view(request, question_id):
    user = request.user
    if not user.is_superuser and user.role not in ['STAFF', 'COACH']:
        return Response({'세부 정보': '이 작업을 수행할 권한이 없습니다.'},
                        status=status.HTTP_403_FORBIDDEN)
