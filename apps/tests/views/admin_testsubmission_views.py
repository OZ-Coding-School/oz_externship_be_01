from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course, Generation, Subject, User
from apps.tests.models import Test, TestDeployment, TestSubmission
from apps.tests.permissions import IsAdminOrStaff
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
            deployment=TestDeployment(
                test=Test(title="프론트엔드 기초 쪽지시험", subject=Subject(title="프론트엔드 기초")),
                generation=Generation(number=3, course=Course(name="프론트 초격차")),
            ),
            student=PermissionsStudent(user=User(name="William", nickname="Will")),
            cheating_count=2,
            # total_score=30, # 시리얼라이저 참고
            started_at="2025-06-26T09:00:00",  # 시험 응시 시간
            created_at="2025-06-26T10:00:00",  # 시험 제출 시간
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
                questions_snapshot_json=[
                    {
                        "question_id": 1,
                        "type": "multiple_choice_single",  # 객관식 단일 선택
                        "question": "HTML의 기본 구조를 이루는 태그는?",
                        "prompt": None,
                        "blank_count": None,
                        "options_json": ["A. <html>", "B. <head>", "C. <body>", "D. <div>"],
                        "answer": ["A"],
                        "point": 5,
                        "explanation": "HTML 문서는 항상 <html> 태그로 시작하여 웹페이지의 전체 구조를 감쌉니다. 이 태그는 문서의 루트 요소로, <head>와 <body>를 포함합니다.",
                    },
                    {
                        "question_id": 2,
                        "type": "ox",  # ox 문제
                        "question": "CSS는 프로그래밍 언어이다.",
                        "prompt": None,
                        "blank_count": None,
                        "options_json": ["O", "X"],
                        "answer": ["X"],
                        "point": 5,
                        "explanation": "CSS는 스타일을 정의하는 선언형 언어이며, 조건문이나 반복문과 같은 로직을 포함하지 않아 일반적으로 프로그래밍 언어로 분류되지 않습니다.",
                    },
                    {
                        "question_id": 3,
                        "type": "ordering",  # 순서 정렬
                        "question": "다음 HTML 요소들을 웹 페이지에 표시되는 순서대로 정렬하세요.",
                        "prompt": None,
                        "blank_count": None,
                        "options_json": ["<head>", "<html>", "<body>", "<title>"],
                        "answer": ["<html>", "<head>", "<body>", "<title>"],
                        "point": 10,
                        "explanation": "HTML 문서는 <html> 태그로 시작하고, 그 안에 <head>와 <body>가 위치합니다. 일반적으로 <head>는 <body>보다 먼저 선언되며, <title>은 <head> 내부에 들어가므로 <html> → <head> → <body> → <title> 순서로 표시되면 안 되고, 구조상 <title>은 <head> 안에 먼저 위치해야 합니다. 정답은 문서 구조의 논리적 순서를 반영해야 합니다.",
                    },
                    {
                        "question_id": 4,
                        "type": "fill_in_blank",  # 빈칸 채우기
                        "question": "다음 문장의 빈칸을 채우세요.",
                        "prompt": "HTML에서 문서의 제목을 설정할 때 사용하는 태그는 <____>이다.",
                        "blank_count": 1,
                        "options_json": [],
                        "answer": ["title"],
                        "point": 5,
                        "explanation": "<title> 태그는 웹 브라우저의 탭이나 검색 엔진 결과에 표시되는 문서의 제목을 정의하는 데 사용됩니다. 이 태그는 <head> 태그 내부에 위치해야 합니다.",
                    },
                    {
                        "question_id": 5,
                        "type": "short_answer",  # 주관식 단답형
                        "question": "다음 문장의 빈칸을 채우세요.",
                        "prompt": "HTML의 <____> 태그는 문서의 제목을 정의하고, <____> 태그 안에 위치한다.",
                        "blank_count": 2,
                        "options_json": [],
                        "answer": ["<title>", "<head>"],
                        "point": 5,
                        "explanation": "color 속성은 HTML 요소의 텍스트 색상을 지정하는 데 사용됩니다. 예를 들어, color: red;는 텍스트 색상을 빨간색으로 설정합니다.",
                    },
                    {
                        "question_id": 6,
                        "type": "multiple_choice_multiple",  # 객관식 다중 선택
                        "question": "다음 중 CSS에서 글자 색상과 관련된 속성을 모두 고르세요.",
                        "prompt": None,
                        "blank_count": None,
                        "options_json": ["A. color", "B. background-color", "C. font-size", "D. text-align"],
                        "answer": ["A", "B"],
                        "point": 5,
                        "explanation": "color는 글자 색상을 지정하고, background-color는 배경 색상을 지정합니다. font-size와 text-align은 각각 글자 크기와 정렬에 관한 속성입니다.",
                    },
                ],
            ),
            cheating_count=2,
            created_at="2025-06-26T09:01:00",
            updated_at="2025-06-26T09:31:00",
            # 모델 필드에는 없음. 응답 JSON에만 포함
            # score=30,           # 총 점수 추가
            # correct_count=5,    # 정답 문제 수
            # total_questions=6,  # 총 문제 수
            # duration_minute=30, # 응시 소요 시간(분)
            answers_json=[
                {"question_id": 1, "type": "multiple_choice_single", "answer": ["A"]},
                {"question_id": 2, "type": "ox", "answer": ["x"]},
                {
                    "question_id": 3,
                    "type": "ordering",
                    "answer": ["<html>", "<head>", "<body>", "<title>"],
                },
                {"question_id": 4, "type": "short_answer", "answer": ["title"]},
                {"question_id": 5, "type": "fill_in_blank", "answer": [""]},
                {"question_id": 6, "type": "multiple_choice_multiple", "answer": ["A", "B"]},
            ],
        )
        serializer = self.serializer_class(instance=mock_data)
        return Response(
            {"message": "쪽지시험 응시내역 목록 상세 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK
        )


# 쪽지 시험 응시 내역 삭제
@extend_schema(tags=["[Admin] Test - submission (쪽지시험 응시 목록/상세/삭제)"])
class AdminTestSubmissionDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def delete(self, request: Request, submission_id: int) -> Response:
        test_submission = get_object_or_404(TestSubmission, pk=submission_id)
        test_submission.delete()
        return Response({"message": f"쪽지시험 응시내역 {submission_id} 삭제 완료"}, status=status.HTTP_200_OK)
