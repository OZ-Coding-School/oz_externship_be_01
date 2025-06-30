from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Generation, Subject
from apps.tests.models import Test, TestDeployment, TestSubmission
from apps.tests.serializers.test_deployment_serializers import UserTestStartSerializer
from apps.tests.serializers.test_submission_serializers import (
    UserTestResultSerializer,
    UserTestSubmitSerializer,
)


# 쪽지 시험 응시
@extend_schema(tags=["[User] Test - submission(쪽지시험 응시/제출/결과조회)"])
class TestSubmissionStartView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserTestStartSerializer

    def post(self, request: Request, test_id: int) -> Response:
        """
        이 API는 쪽지 시험 응시를 위한 test_id, access_code의 유효성을 판별합니다.
        :param request: test_id, access_code
        :return: 생략
        """

        access_code = "abc123"

        # 클라이언트가 요청한 값
        data = request.data

        # mock data
        mock_data = TestDeployment(
            id=1,
            generation=Generation(id=1),
            test=Test(
                id=test_id,
                title="프론트엔드 기초 쪽지시험",
                subject=Subject(id=1, title="프론트엔드 기초"),
                thumbnail_img_url="https://cdn.example.com/images/frontend_basic_quiz_thumbnail.png",
            ),
            duration_time=60,
            questions_snapshot_json=[
                {
                    "question_id": 1,
                    "type": "multiple_choice",  # 객관식
                    "question": "HTML의 기본 구조를 이루는 태그는?",
                    "prompt": None,
                    "blank_count": None,
                    "options_json": ["A. <html>", "B. <head>", "C. <body>", "D. <div>"],
                    "point": 5,
                },
                {
                    "question_id": 2,
                    "type": "ox",  # "ox문제"
                    "question": "CSS는 프로그래밍 언어이다.",
                    "prompt": None,
                    "blank_count": None,
                    "options_json": ["O", "X"],
                    "point": 5,
                },
                {
                    "question_id": 3,
                    "type": "ordering",  # 순서 정렬"
                    "question": "다음 HTML 요소들을 웹 페이지에 표시되는 순서대로 정렬하세요.",
                    "prompt": None,
                    "blank_count": None,
                    "options_json": ["<head>", "<html>", "<body>", "<title>"],
                    "point": 5,
                },
                {
                    "question_id": 4,
                    "type": "fill_in_blank",  # 빈칸 채우기
                    "question": "다음 문장의 빈칸을 채우세요.",
                    "prompt": "HTML에서 문서의 제목을 설정할 때 사용하는 태그는 <____>이다.",
                    "blank_count": 1,
                    "options_json": [],
                    "point": 5,
                },
                {
                    "question_id": 5,
                    "type": "fill_in_blank",  # 빈칸 채우기
                    "question": "다음 문장의 빈칸을 채우세요.",
                    "prompt": "HTML의 <____> 태그는 문서의 제목을 정의하고, <____> 태그 안에 위치한다.",
                    "blank_count": 2,
                    "options_json": [],
                    "point": 5,
                },
            ],
        )

        # 유효성 검증
        # request.data에 access_code가 없으면 에러 반환
        if "access_code" not in data:
            return Response({"message": "시험 코드를 입력해 주세요."}, status=400)

        # access_code 불일치 시 에러 반환
        if access_code != data.get("access_code"):
            return Response({"message": "등록 되지 않은 시험 코드 입니다."}, status=403)

        serializer = self.serializer_class(mock_data)
        return Response({"message": "쪽지시험 응시 시작 완료", "data": serializer.data}, status=status.HTTP_200_OK)


# 쪽지 시험 제출
@extend_schema(
    tags=["[User] Test - submission(쪽지시험 응시/제출/결과조회)"],
    request=UserTestSubmitSerializer,
    examples=[
        OpenApiExample(
            name="제출 예시",
            value={
                "id": 1,
                "deployment": 1,
                "started_at": "2025-06-20T10:30:00",
                "cheating_count": 2,
                "answers_json": [
                    # 객관식
                    {"question_id": 1, "answer": ["A"]},
                    # ox 문제
                    {"question_id": 2, "answer": ["x"]},
                    # 순서 정렬 답안
                    {"question_id": 3, "answer": ["<html>", "<head>", "<body>", "<title>"]},
                    # 빈칸 채우기
                    {"question_id": 4, "answer": ["title"]},
                    # 미작성
                    {"question_id": 5, "answer": [""]},
                ],
            },
        )
    ],
)
class TestSubmissionSubmitView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserTestSubmitSerializer

    def post(self, request: Request, deployment_id: int) -> Response:
        # 클라이언트가 요청한 값
        data = request.data

        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response(
                {"message": "유효하지 않은 데이터입니다.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "쪽지시험 제출 완료", "data": serializer.data}, status=status.HTTP_200_OK)


# 쪽지 시험 결과 조회
@extend_schema(tags=["[User] Test - submission(쪽지시험 응시/제출/결과조회)"])
class TestSubmissionResultView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserTestResultSerializer

    def get(self, request: Request, submission_id: int) -> Response:
        mock_data = TestSubmission(
            id=1,
            cheating_count=1,
            answers_json={
                "1": ["A"],
                "2": ["x"],
                "3": ["<html>", "<head>", "<body>", "<title>"],
                "4": ["title"],
                "5": [""],
            },
            deployment=TestDeployment(
                id=10,
                test=Test(
                    id=5,
                    title="CSS 기초 진단 평가",
                    thumbnail_img_url="https://example.com/images/css-test.jpg",
                ),
                questions_snapshot_json=[
                    {
                        "question_id": 1,
                        "type": "multiple_choice",
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
                        "type": "ox",
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
                        "type": "ordering",
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
                        "type": "fill_in_blank",
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
                        "type": "빈칸 채우기",
                        "question": "다음 문장의 빈칸을 채우세요.",
                        "prompt": "HTML의 <____> 태그는 문서의 제목을 정의하고, <____> 태그 안에 위치한다.",
                        "blank_count": 2,
                        "options_json": [],
                        "answer": ["<title>", "<head>"],
                        "point": 5,
                        "explanation": "color 속성은 HTML 요소의 텍스트 색상을 지정하는 데 사용됩니다. 예를 들어, color: red;는 텍스트 색상을 빨간색으로 설정합니다.",
                    },
                ],
            ),
        )

        serializer = self.serializer_class(instance=mock_data)
        return Response({"message": "쪽지시험 결과 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK)
