from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response


# 쪽지시험 응시 API
@extend_schema(tags=["Tests"])
@api_view(["POST"])
@permission_classes([AllowAny])
def post_test_submission_start(request: Request) -> Response:

    # 임시 데이터 (목 API용)
    mock_data = {
        "test_id": 4,
        "access_code": "ABC123XYZ",
        "title": "프론트엔드 기초 쪽지시험",
        "thumbnail_img_url": "https://...",
        "elapsed_time": 30,
        "cheating_count": 0,
        "questions": [
            {
                "question_id": 1,
                "type": "객관식",
                "question": "HTML의 기본 구조를 이루는 태그는?",
                "options": ["<html>", "<head>", "<body>", "<div>"],
                "point": 5,
            },
            {
                "question_id": 2,
                "type": "O/X",
                "question": "CSS는 프로그래밍 언어이다.",
                "options": ["O", "X"],
                "point": 5,
            },
        ],
    }

    return Response({"message": "쪽지시험 응시 시작 완료", "data": mock_data}, status=status.HTTP_200_OK)


# 쪽지시험 제출 API
@extend_schema(tags=["Tests"])
@api_view(["POST"])
@permission_classes([AllowAny])
# @permission_classes(['IsAuthenticated'])
def post_test_submission_submit(request: Request, submission_id: int) -> Response:
    mock_data = {
        "submission_id": 1,
        "student_id": 101,
        "deployment_id": 15,
        "started_at": "2025-06-20T10:30:00",
        "cheating_count": 2,
        "answers": [{"question_id": 201, "answer": ["A"]}, {"question_id": 202, "answer": []}],
    }

    return Response({"message": "쪽지시험 제출 완료", "data": mock_data}, status=status.HTTP_200_OK)


# 쪽지시험 결과조회 API
@extend_schema(tags=["Tests"])
@api_view(["GET"])
@permission_classes([AllowAny])
def get_test_submission_result(request: Request, submission_id: int) -> Response:

    mock_data = {
        "submission_id": 1,
        "test_title": "CSS 기초 진단 평가",
        "test_thumbnail_img_url": "https://example.com/images/css-test.jpg",
        "total_questions": 3,
        "questions": [
            {
                "question_id": 101,
                "type": "multiple_choice",
                "question": "CSS의 주요 역할은 무엇인가요?",
                "prompt": None,
                "blank_count": None,
                "options": ["디자인", "기능", "구조", "스타일"],
                "student_answer": ["디자인"],
                "correct_answer": ["디자인"],
                "point": 5,
                "explanation": "CSS는 웹페이지의 스타일을 정의합니다.",
                "is_correct": True,
            },
            {
                "question_id": 102,
                "type": "ox",
                "question": "CSS는 프로그래밍 언어이다.",
                "options": ["O", "X"],
                "student_answer": ["O"],
                "correct_answer": ["X"],
                "point": 5,
                "explanation": "CSS는 선언형 언어로 프로그래밍 언어가 아닙니다.",
                "is_correct": False,
            },
            {
                "question_id": 103,
                "type": "subjective",
                "question": "CSS의 박스 모델에 대해 설명하시오.",
                "student_answer": ["margin, border, padding, content 순서입니다."],
                "correct_answer": ["margin, border, padding, content 순서입니다."],
                "point": 10,
                "explanation": "정확하게 서술됨.",
                "is_correct": True,
            },
        ],
        "cheating_count": 1,
    }

    return Response({"message": "쪽지시험 결과 조회 완료", "data": mock_data}, status=status.HTTP_200_OK)
