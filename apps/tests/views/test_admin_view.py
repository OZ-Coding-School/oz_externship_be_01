from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import TestSubmission
from apps.tests.serializers.admin_submission_serializers import TestStartSerializer


# 쪽지시험 응시내역 목록 조회
@extend_schema(tags=["Tests/Admin"])
class AdminTestSubmissionsView(APIView):
    permission_classes = [AllowAny]
    serializers_class = TestStartSerializer

    def get(self, request: Request, submission_id: int) -> Response:
        # mock_data = TestSubmission(
        #     id=1,
        #     cheating_count=2,
        #     started_at="2025-06-26T09:01:00",
        # )
        mock_data = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "submission_id": 101,
                    "student": {"nickname": "codeMaster", "name": "홍길동", "generation": "프론트엔드 5기"},
                    "test": {"title": "HTML 기초 테스트", "subject_title": "웹프로그래밍"},
                    "score": 85,
                    "cheating_count": 1,
                    "started_at": "2025-06-21T09:01:00",
                    "submitted_at": "2025-06-21T09:29:00",
                },
                {
                    "submission_id": 102,
                    "student": {"nickname": "devStar", "name": "김영희", "generation": "백엔드 4기"},
                    "test": {"title": "JavaScript 테스트", "subject_title": "프론트엔드"},
                    "score": 92,
                    "cheating_count": 0,
                    "started_at": "2025-06-20T13:00:00",
                    "submitted_at": "2025-06-20T13:29:00",
                },
            ],
        }

        serializer = TestStartSerializer(instance=mock_data)
        return Response({"data": mock_data, "message": "쪽지시험 응시내역 목록 조회 완료"}, status=status.HTTP_200_OK)


# 쪽지시험 응시내역 상세 조회 및 삭제 MockAPI
@extend_schema(tags=["Tests/Admin"])
class AdminTestSubmissionDetailDeleteView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, submission_id: int) -> Response:
        mock_data = {
            "submission_id": submission_id,
            "test_title": "HTML/CSS 기초",
            "subject_title": "웹프로그래밍",
            "duration_time": 30,
            "open_at": "2025-06-21T09:00:00",
            "close_at": "2025-06-21T09:30:00",
            "student": {"nickname": "codeMaster", "name": "홍길동", "generation": "프론트엔드 5기"},
            "score": 85,
            "correct_count": 8,
            "total_questions": 10,
            "cheating_count": 1,
            "started_at": "2025-06-21T09:01:00",
            "submitted_at": "2025-06-21T09:29:00",
            "answers": [
                {
                    "question_id": 101,
                    "type": "객관식",
                    "question": "HTML에서 제목 태그는 무엇인가요?",
                    "point": 10,
                    "correct_answer": "<h1>",
                    "student_answer": "<h1>",
                    "is_correct": True,
                },
                {
                    "question_id": 102,
                    "type": "주관식",
                    "question": "CSS에서 색상 지정 방법을 2가지 이상 쓰시오.",
                    "point": 10,
                    "correct_answer": "hex, rgb, hsl",
                    "student_answer": "hex, rgb",
                    "is_correct": True,
                },
            ],
        }

        serializer = TestStartSerializer(data=mock_data)
        if serializer.is_valid():
            return Response(
                {"data": serializer.data, "message": "쪽지시험 응시내역 상세 조회 완료"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "유효하지 않은 데이터입니다.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request: Request, submission_id: int) -> Response:
        # 실제 삭제 로직 있으면 여기서 처리
        return Response({"message": f"쪽지시험 응시내역 {submission_id} 삭제 완료"}, status=status.HTTP_200_OK)
