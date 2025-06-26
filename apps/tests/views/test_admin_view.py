from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from datetime import datetime
from rest_framework.permissions import AllowAny
from apps.tests.serializers.user_admin_deployment_serializers import CodeValidationRequestSerializer, \
    DeploymentListSerializer, DeploymentDetailSerializer, DeploymentCreateSerializer

# MOCK 데이터 (변경 가능하도록 global 선언)
MOCK_DEPLOYMENTS = [
    {
        "deployment_id": 101,
        "test_title": "HTML 기초",
        "subject_title": "웹프로그래밍",
        "course_generation": "웹프로그래밍 5기",
        "total_participants": 15,
        "average_score": 85.6,
        "status": "Activated",
        "created_at": "2025-06-19T09:00:00"
    },
    {
        "deployment_id": 102,
        "test_title": "CSS 심화",
        "subject_title": "웹디자인",
        "course_generation": "웹디자인 4기",
        "total_participants": 10,
        "average_score": 78.2,
        "status": "Deactivated",
        "created_at": "2025-06-18T13:30:00"
    }
]

MOCK_DEPLOYMENTS_DETAILS = {
    101: {
        "test": {
            "test_id": 101,
            "test_title": "HTML 기초",
            "subject_title": "웹프로그래밍",
            "question_count": 10
        },
        "deployment": {
            "deployment_id": 101,
            "access_url": "https://ozclass.com/exam/101",
            "access_code": "aB3dE9",
            "course_title": "웹프로그래밍 올인원 과정",
            "generation_title": "5기",
            "duration_time": 60,
            "open_at": "2025-06-19T09:00:00",
            "close_at": "2025-06-19T10:00:00",
            "status": "Activated",
            "created_at": "2025-06-18T12:00:00",
            "updated_at": "2025-06-18T18:30:00"
        },
        "submission_stats": {
            "total_participants": 15,
            "not_participated": 2
        }
    },
    102: {
        "test": {
            "test_id": 102,
            "test_title": "CSS 심화",
            "subject_title": "웹디자인",
            "question_count": 8
        },
        "deployment": {
            "deployment_id": 102,
            "access_url": "https://ozclass.com/exam/102",
            "access_code": "Zx81Lm",
            "course_title": "웹디자인 포트폴리오 캠프",
            "generation_title": "4기",
            "duration_time": 45,
            "open_at": "2025-06-18T13:30:00",
            "close_at": "2025-06-18T14:15:00",
            "status": "Deactivated",
            "created_at": "2025-06-17T10:00:00",
            "updated_at": "2025-06-17T16:45:00"
        },
        "submission_stats": {
            "total_participants": 10,
            "not_participated": 1
        }
    }
}
# 공용
def paginate_response(request, data, serializer_class):
    q = request.query_params # URL 쿼리스트링 파라미터를 가져옴
    s = q.get("search", "").lower()
    if s:
        data = [d for d in data if s in d["test_title"].lower() or s in d["subject_title"].lower()]
    ordering = q.get("ordering", "-created_at")
    reverse, key = ordering.startswith("-"), ordering.lstrip("-")
    if data and key in data[0]:
        # key 필드 기준으로 정렬
        data.sort(key=lambda x: x.get(key), reverse=reverse)
    # 페이지네이션 설정
    paginator = PageNumberPagination()
    paginator.page_size = int(q.get("page_size", 10)) if q.get("page_size", "").isdigit() else 10
    page = paginator.paginate_queryset(data, request)
    return paginator.get_paginated_response(serializer_class(page, many=True).data)


@extend_schema(
    methods=["POST"],
    description="관리자용 참가코드 검증 MOCK API",
    request=CodeValidationRequestSerializer,
    responses={200: dict, 400: dict},
    tags=["test"],
)
#참가코드 기능 구현
class TestValidateCodeAdminView(APIView):
    permission_classes = [AllowAny]  # ← 인증 없이 접근 허용 (MOCK API용)
    def post(self, request):
        serializer = CodeValidationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        deployment_id = data["deployment_id"]
        access_code = data["access_code"]

        details = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)

        if (
            details
            and details["deployment"]["access_code"] == access_code
            and details["deployment"]["status"] == "Activated"
        ):
            return Response({
                "message": "참가코드가 유효합니다.",
                "test_title": details["test"]["test_title"],
                "deployment_id": deployment_id,
                "duration_time": details["deployment"]["duration_time"]
            })

        return Response({"detail": "유효하지 않은 참가코드입니다."}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    methods=["PATCH"],
    parameters=[OpenApiParameter("deployment_id", int, OpenApiParameter.PATH)],
    responses={200: dict, 404: dict},
    description="쪽지시험 배포 상태 토글 MOCK API",
    tags=["test"],
)
#배포
class TestDeploymentStatusView(APIView):
    permission_classes = [AllowAny]  # ← 인증 없이 접근 허용 (MOCK API용)
    def patch(self, request, deployment_id):
        # MOCK_DEPLOYMENTS 리스트에서 해당 배포 찾기
        deployment = next((d for d in MOCK_DEPLOYMENTS if d["deployment_id"] == deployment_id), None)
        details = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)

        if not deployment or not details:
            # 없으면 에러 404 에러
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 상태 토글
        current_status = deployment["status"]
        new_status = "Deactivated" if current_status == "Activated" else "Activated"

        deployment["status"] = new_status
        details["status"] = new_status

        return Response({
            "deployment_id": deployment_id,
            "status": new_status,
            "message": "배포 상태가 성공적으로 변경되었습니다."
        })

@extend_schema(
    methods=["POST"],
    description="관리자용 쪽지시험 배포 생성 API",
    request=DeploymentCreateSerializer,
    responses={
        201: {"deployment_id": 123,"access_code": "Ab12CD","status": "Activated"},
        400: {"detail": "Invalid request data."},
    },
    tags=["test"],
)
# 쪽지시험 배포 생성
class TestDeploymentCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DeploymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "deployment_id": 123,
            "access_code": "Ab12CD",
            "status": "Activated"
        },status=status.HTTP_201_CREATED)



@extend_schema(
    methods=["DELETE"],
    parameters=[OpenApiParameter("deployment_id", int, OpenApiParameter.PATH)],
    responses={204: None, 404: dict},
    description="쪽지시험 배포 삭제 MOCK API",
    tags=["test"],
)
# 배포 삭제
class DeleteMiniTestDeploymentView(APIView):
    permission_classes = [AllowAny]  # ← 인증 없이 접근 허용 (MOCK API용)
    def delete(self, request, deployment_id):
        global MOCK_DEPLOYMENTS, MOCK_DEPLOYMENTS_DETAILS

        deployment_index = next((i for i, d in enumerate(MOCK_DEPLOYMENTS) if d["deployment_id"] == deployment_id), None)

        if deployment_index is None or deployment_id not in MOCK_DEPLOYMENTS_DETAILS:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 삭제 처리 (리스트/딕셔너리에서 삭제)
        del MOCK_DEPLOYMENTS[deployment_index]
        del MOCK_DEPLOYMENTS_DETAILS[deployment_id]

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter("search", str, required=False),
        OpenApiParameter("ordering", str, required=False),
        OpenApiParameter("page_size", int, required=False),
    ],
    tags=["test"],
)
class DeploymentListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return paginate_response(request, MOCK_DEPLOYMENTS, DeploymentListSerializer)

#  배포 내역 조회 API

@extend_schema(
    methods=["GET"],
    parameters=[OpenApiParameter("deployment_id", int, OpenApiParameter.PATH)],
    responses={200: DeploymentDetailSerializer, 404: dict},
    description="관리자용 쪽지시험 배초 상세 조회 MOCK API",
    tags=["test"],
)
class DeploymentDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, deployment_id):
        # MOCK 데이터에서 조회
        raw_data = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)
        if not raw_data:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)
        #  직렬화 및 응답
        serializer = DeploymentDetailSerializer(instance=raw_data)
        return Response(serializer.data)
