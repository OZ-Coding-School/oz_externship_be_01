from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Generation, Subject, User
from apps.tests.models import Test, TestDeployment, TestSubmission
from apps.tests.permissions import IsStudent
from apps.tests.serializers.test_deployment_serializers import (
    UserTestDeploymentSerializer,
    UserTestStartSerializer,
)
from apps.tests.serializers.test_submission_serializers import (
    UserTestResultSerializer,
    UserTestSubmitSerializer,
)
from apps.users.models import PermissionsStudent


# 쪽지 시험 응시
@extend_schema(
    tags=["[User] Test - submission (쪽지시험 응시/제출/결과조회)"],
    request=UserTestStartSerializer,
)
class TestSubmissionStartView(APIView):
    permission_classes = [IsAuthenticated]
    request_serializer_class = UserTestStartSerializer
    response_serializer_class = UserTestDeploymentSerializer

    def post(self, request: Request, test_id: int) -> Response:
        """
        이 API는 쪽지 시험 응시를 위한 test_id, access_code의 유효성을 판별합니다.
        """
        serializer = self.request_serializer_class(data=request.data, context={"test_id": test_id})
        serializer.is_valid(raise_exception=True)

        access_code = serializer.validated_data["access_code"]
        deployment = get_object_or_404(TestDeployment, access_code=access_code, test_id=test_id)

        response_serializer = self.response_serializer_class(instance=deployment)
        return Response(
            {"message": "Test started successfully.", "data": response_serializer.data}, status=status.HTTP_200_OK
        )


# 수강생 쪽지 시험 제출
@extend_schema(
    tags=["[User] Test - submission (쪽지시험 응시/제출/결과조회)"],
    request=UserTestSubmitSerializer,
)
class TestSubmissionSubmitView(APIView):
    # permission_classes = [AllowAny]
    permission_classes = [IsStudent]
    serializer_class = UserTestSubmitSerializer

    def post(self, request: Request, deployment_id: int) -> Response:
        """
        쪽지 시험 제출 API
        """
        try:
            deployment = TestDeployment.objects.get(id=deployment_id)
        except TestDeployment.DoesNotExist:
            return Response({"detail": "배포된 시험이 존재하지 않습니다."}, status=404)

        # try:
        #     student = PermissionsStudent.objects.filter(user=request.user.id).first()
        #     print(student)
        #     if not student:
        #         return Response({"detail": "수강생 정보가 없습니다?????????????."}, status=400)
        # except Exception as e:
        #     return Response({"detail": str(e)}, status=400)

        student_id = request.data.get("student_id")
        if not student_id:
            return Response({"detail": "student_id가 필요합니다."}, status=400)

        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "로그인한 사용자만 접근 가능합니다."}, status=401)

        try:
            student = PermissionsStudent.objects.get(user=request.user)
        except PermissionsStudent.DoesNotExist:
            return Response({"detail": "수강생 정보가 없습니다."}, status=400)

        # try:
        #     # 인증된 사용자여야 함
        #     user = request.user
        #     # if not user.is_authenticated:
        #     #     return Response({"detail": "인증이 필요합니다."}, status=401)
        #
        #     # 역할 체크 (선택 사항)
        #     if user.role != User.Role.STUDENT:
        #         return Response({"detail": "수강생 권한이 필요합니다."}, status=403)
        #
        #     # PermissionsStudent 객체 조회
        #     student = PermissionsStudent.objects.filter(user=user).first()
        #     if not student:
        #         return Response({"detail": "수강생 정보가 없습니다."}, status=400)
        #
        # except Exception as e:
        #     return Response({"detail": str(e)}, status=400)

        data = request.data.copy()

        serializer = self.serializer_class(
            data=data, context={"request": request, "deployment": deployment, "student": student}
        )
        serializer.is_valid(raise_exception=True)

        now = timezone.now()

        # 시험 제출 시간 만료 시 자동 제출 처리
        if deployment.close_at and deployment.close_at < now:
            serializer.save(started_at=now, deployment=deployment)
            return Response({"detail": "시험 제출 시간이 지나 자동 제출 되었습니다."}, status=status.HTTP_200_OK)

        # 부정행위 3회 이상 적발 시 자동 제출
        cheating_count = data.get("cheating_count")
        if cheating_count is not None and int(cheating_count) >= 3:
            serializer.save(started_at=now, deployment=deployment)
            return Response({"detail": "부정행위 3회 이상 적발되어 자동 제출 처리되었습니다."})

        # db 저장s
        serializer.save(started_at=now, deployment=deployment)
        return Response({"message": "시험 제출이 완료되었습니다."}, status=status.HTTP_200_OK)


# 쪽지 시험 결과 조회
@extend_schema(tags=["[User] Test - submission (쪽지시험 응시/제출/결과조회)"])
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
        )

        serializer = self.serializer_class(instance=mock_data)
        return Response({"message": "쪽지시험 결과 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK)
