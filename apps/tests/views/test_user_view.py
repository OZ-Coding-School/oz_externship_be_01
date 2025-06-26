from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Generation
from apps.tests.models import Test, TestDeployment, TestQuestion, TestSubmission
from apps.tests.serializers.submission_result_serializers import TestResultSerializer
from apps.tests.serializers.submission_start_serializers import (
    TestStartSerializer,
)
from apps.tests.serializers.submission_submit_serializers import TestSubmitSerializer


# 쪽지 시험 응시
@extend_schema(tags=["Tests"])
class TestSubmissionStartView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TestStartSerializer

    def post(self, request: Request, test_id: int) -> Response:
        """
        이 API는 쪽지 시험 응시를 위한 test_id, access_code의 유효성을 판별합니다.
        :param request: test_id, access_code
        :return: 생략
        """
        # 클라이언트가 요청한 값
        data = request.data

        # mock data
        mock_data = TestDeployment(
            id=1,
            generation=Generation(id=1),
            test=Test(
                id=test_id,
                title="프론트엔드 기초 쪽지시험",
                thumbnail_img_url="https://...",
            ),
            duration_time=60,
            access_code="abc123",
            open_at="2025-06-25T15:00:00",
            close_at="2025-06-25T16:00:00",
            questions_snapshot_json=[
                {
                    "question_id": 1,
                    "type": "객관식",
                    "question": "HTML의 기본 구조를 이루는 태그는?",
                    "options_json": ["<html>", "<head>", "<body>", "<div>"],
                    "point": 5,
                },
                {
                    "question_id": 2,
                    "type": "O/X",
                    "question": "CSS는 프로그래밍 언어이다.",
                    "options_json": ["O", "X"],
                    "point": 5,
                },
            ],
            status="Activated",
            created_at="2025-06-25T15:00:00",
            updated_at="2025-06-25T16:00:00",
        )

        # 유효성 검증
        # request.data에 access_code가 없으면 에러 반환
        if "access_code" not in data:
            return Response({"message": "시험 코드를 입력해 주세요."}, status=400)

        # access_code 불일치 시 에러 반환
        if mock_data.access_code != data.get("access_code"):
            return Response({"message": "등록 되지 않은 시험 코드 입니다."}, status=403)

        serializer = self.serializer_class(mock_data)
        return Response({"message": "쪽지시험 응시 시작 완료", "data": serializer.data}, status=status.HTTP_200_OK)


# 쪽지 시험 제출
@extend_schema(
    tags=["Tests"],
    request=TestSubmitSerializer,
    examples=[
        OpenApiExample(
            name="제출 예시",
            value={
                "id": 1,
                "deployment": 1,
                "started_at": "2025-06-20T10:30:00",
                "cheating_count": 2,
                "answers_json": [{"question_id": 201, "answer": ["A"]}, {"question_id": 202, "answer": ["B"]}],
                "created_at": "2025-06-25T15:00:00",
                "updated_at": "2025-06-25T16:00:00",
            },
        )
    ],
)
class TestSubmissionSubmitView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TestSubmitSerializer

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
class TestSubmissionResultView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TestResultSerializer

    @extend_schema(tags=["Tests"])
    def get(self, request: Request, submission_id: int) -> Response:
        mock_data = TestSubmission(
            id=1,
            cheating_count=1,
            answers_json={"101": ["디자인"], "102": ["O"], "103": ["margin, border, padding, content 순서입니다."]},
            deployment=TestDeployment(
                id=10,
                test=Test(
                    id=5,
                    title="CSS 기초 진단 평가",
                    thumbnail_img_url="https://example.com/images/css-test.jpg",
                ),
                questions_snapshot_json=[
                    {
                        "question_id": 101,
                        "type": "multiple_choice",
                        "question": "CSS의 주요 역할은 무엇인가요?",
                        "prompt": None,
                        "blank_count": None,
                        "options_json": ["디자인", "기능", "구조", "스타일"],
                        "answer": ["디자인"],
                        "point": 5,
                        "explanation": "CSS는 웹페이지의 스타일을 정의합니다.",
                        "is_correct": True,
                    },
                    {
                        "question_id": 102,
                        "type": "ox",
                        "question": "CSS는 프로그래밍 언어이다.",
                        "options_json": ["O", "X"],
                        "answer": ["X"],
                        "point": 5,
                        "explanation": "CSS는 선언형 언어로 프로그래밍 언어가 아닙니다.",
                        "is_correct": False,
                    },
                    {
                        "question_id": 103,
                        "type": "subjective",
                        "question": "CSS의 박스 모델에 대해 설명하시오.",
                        "answer": ["margin, border, padding, content 순서입니다."],
                        "point": 10,
                        "explanation": "정확하게 서술됨.",
                        "is_correct": True,
                    },
                ],
            ),
        )

        serializer = self.serializer_class(instance=mock_data)
        return Response({"message": "쪽지시험 결과 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK)
