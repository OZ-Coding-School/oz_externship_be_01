from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course, Generation, Subject, User
from apps.tests.models import Test, TestDeployment, TestSubmission
from apps.tests.serializers.admin_submission_detail_serializers import (
    TestDetailSerializer,
)
from apps.tests.serializers.admin_submission_serializers import TestListSerializer
from apps.users.models.permissions import PermissionsStudent


# 쪽지 시험 응시 내역 전체 목록 조회
@extend_schema(tags=["Tests/Admin"])
class AdminTestSubmissionsView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TestListSerializer

    def get(self, request: Request) -> Response:
        mock_data = TestSubmission(
            id=1,
            cheating_count=2,
            started_at="2025-06-26T09:01:00",
            student=PermissionsStudent(id=1, user=User(id=1, name="William", nickname="Will")),
            deployment=TestDeployment(
                id=1,
                generation=Generation(id=1, number=3, course=Course(id=1, name="백엔드 트랙")),
                test=Test(id=1, title="자료구조 기초 테스트", subject=Subject(id=1, title="자료구조")),
            ),
        )

        serializer = self.serializer_class(instance=mock_data)
        return Response(
            {"message": "쪽지시험 응시내역 목록 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK
        )


# 쪽지 시험 응시 내역 상세 조회
@extend_schema(tags=["Tests/Admin"])
class AdminTestSubmissionDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TestDetailSerializer

    def get(self, request: Request, submission_id: int) -> Response:
        mock_data = TestSubmission(
            id=1,
            cheating_count=2,
            started_at="2025-06-26T09:01:00",
            answers_json=[
                {"question_id": 1, "answer": "A"},
                {"question_id": 2, "answer": "B"},
            ],
            student=PermissionsStudent(id=1, user=User(id=1, name="William", nickname="Will")),
            deployment=TestDeployment(
                id=1,
                duration_time=30,
                open_at="2025-06-01T00:00:00",
                close_at="2025-06-01T00:00:00",
                questions_snapshot_json=[
                    {
                        "id": 1,
                        "question": "자료구조의 정의는?",
                        "options_json": ["A. 자료의 구조", "B. 알고리즘", "C. 컴파일러", "D. 하드웨어"],
                        "type": "객관식",
                        "answer": "A",
                        "point": 10,
                    }
                ],
                generation=Generation(id=1, number=3, course=Course(id=1, name="백엔드 트랙")),
                test=Test(
                    id=1,
                    title="자료구조 기초 테스트",
                    subject=Subject(id=1, title="자료구조"),
                    created_at="2025-06-01T00:00:00",
                    updated_at="2025-06-01T00:00:00",
                ),
            ),
        )

        serializer = self.serializer_class(instance=mock_data)
        return Response(
            {"message": "쪽지시험 응시내역 목록 상세 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK
        )


# 쪽지 시험 응시 내역 삭제
@extend_schema(tags=["Tests/Admin"])
class AdminTestSubmissionDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request: Request, submission_id: int) -> Response:

        return Response({"message": f"쪽지시험 응시내역 {submission_id} 삭제 완료"}, status=status.HTTP_200_OK)
