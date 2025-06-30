from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course, Generation, Subject, User
from apps.tests.models import Test, TestDeployment, TestSubmission
from apps.tests.serializers.test_submission_serializers import (
    AdminTestDetailSerializer,
    AdminTestListSerializer,
)
from apps.users.models.permissions import PermissionsStudent


# 쪽지 시험 응시 내역 전체 목록 조회
@extend_schema(tags=["[Admin] Test - submission (쪽지시험 응시 목록/상세/삭제)"])
class AdminTestSubmissionsView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminTestListSerializer

    def get(self, request: Request) -> Response:
        mock_data = TestSubmission(
            id=1,
            student=PermissionsStudent(id=1, user=User(id=1, name="William", nickname="Will")),
            deployment=TestDeployment(
                id=1,
                generation=Generation(id=1, number=3, course=Course(id=1, name="프론트 초격차")),
                test=Test(id=1, title="프론트엔드 기초 쪽지시험", subject=Subject(id=1, title="프론트엔드 기초")),
            ),
            cheating_count=2,
            # 모델 필드에는 없음. 응답 JSON에만 포함
            # score=85,
            created_at="2025-06-26T09:00:00",
            updated_at="2025-06-26T10:00:00",
        )

        serializer = self.serializer_class(instance=mock_data)
        return Response(
            {"message": "쪽지시험 응시내역 목록 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK
        )


# 쪽지 시험 응시 내역 상세 조회
@extend_schema(tags=["[Admin] Test - submission (쪽지시험 응시 목록/상세/삭제)"])
class AdminTestSubmissionDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminTestDetailSerializer

    def get(self, request: Request, submission_id: int) -> Response:
        mock_data = TestSubmission(
            id=1,
            student=PermissionsStudent(id=1, user=User(id=1, name="William", nickname="Will")),
            deployment=TestDeployment(
                id=1,
                duration_time=30,
                open_at="2025-06-01T00:00:00",
                close_at="2025-06-01T00:00:00",
                generation=Generation(id=1, number=3, course=Course(id=1, name="프론트 초격차")),
                test=Test(
                    id=1,
                    title="프론트엔드 기초 쪽지시험",
                    subject=Subject(id=1, title="프론트엔드 기초"),
                ),
            ),
            cheating_count=2,
            created_at="2025-06-26T09:01:00",
            updated_at="2025-06-26T09:31:00",
            # 모델 필드에는 없음. 응답 JSON에만 포함
            # score=85,
            # correct_count=9,
            # total_questions=10,
            answers_json=[
                {"question_id": 1, "type": "multiple_choice", "point": 5, "answer": ["A"]},
                {"question_id": 2, "type": "ox", "point": 5, "answer": ["X"]},
                {
                    "question_id": 3,
                    "type": "ordering",
                    "point": 10,
                    "answer": ["<html>", "<head>", "<body>", "<title>"],
                },
                {"question_id": 4, "type": "fill_in_blank", "point": 5, "answer": ["title"]},
                {"question_id": 5, "type": "fill_in_blank", "point": 5, "answer": [""]},
            ],
        )
        serializer = self.serializer_class(instance=mock_data)
        return Response(
            {"message": "쪽지시험 응시내역 목록 상세 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK
        )


# 쪽지 시험 응시 내역 삭제
@extend_schema(tags=["[Admin] Test - submission (쪽지시험 응시 목록/상세/삭제)"])
class AdminTestSubmissionDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request: Request, submission_id: int) -> Response:

        return Response({"message": f"쪽지시험 응시내역 {submission_id} 삭제 완료"}, status=status.HTTP_200_OK)
