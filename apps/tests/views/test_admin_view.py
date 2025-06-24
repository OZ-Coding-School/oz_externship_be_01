from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response


# 쪽지시험 응시내역 목록 조회 MockAPI
@extend_schema(tags=["Tests/Admin"])
@api_view(["GET"])
@permission_classes([AllowAny])
def admin_test_submissions(request: Request) -> Response:
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

    return Response({"data": mock_data, "message": "쪽지시험 응시내역 목록 조회 완료"}, status=status.HTTP_200_OK)


# 쪽지시험 응시내역 상세 조회 및 삭제 MockAPI
@extend_schema(tags=["Tests/Admin"])
@api_view(["GET", "DELETE"])
@permission_classes([AllowAny])
def admin_test_submissions_detail(request: Request, submission_id: int) -> Response:
    if request.method == "GET":
        mock_data = {
            "submission_id": 1,
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
        return Response({"data": mock_data, "message": "쪽지시험 응시내역 상세 조회 완료"}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        return Response({"message": f"쪽지시험 응시내역 {submission_id} 삭제 완료"}, status=status.HTTP_200_OK)

    return Response({"detail": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# 쪽지시험 응시내역 삭제 MockAPI
# @extend_schema(tags=["Tests/Admin"])
# @api_view(["DELETE"])
# @permission_classes([AllowAny])
# def admin_test_submissions_delete(request, submission_id):
#     return Response({"message": f"쪽지시험 응시내역 {submission_id} 삭제 완료"}, status=status.HTTP_200_OK)
