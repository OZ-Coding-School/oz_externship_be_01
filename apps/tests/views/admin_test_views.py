import datetime
import uuid
from typing import Any, Dict, cast

import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import parsers, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Subject

# 내부 앱 - models
from apps.tests.models import Test, TestQuestion
from apps.tests.permissions import IsAdminOrStaff
from apps.tests.serializers.test_serializers import (
    AdminTestUpdateSerializer,
    TestCreateSerializer,
    TestDetailSerializer,
    TestListSerializer,
    TestQuestionSimpleSerializer,
)
from apps.users.models import User


@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 삭제 API",
    description=(
        "관리자 또는 스태프 권한으로 특정 쪽지시험(Test)을 삭제합니다.\n"
        "- 연결된 문제(TestQuestion)는 함께 삭제되며,\n"
        "- 배포(TestDeployment), 응시(TestSubmission)는 보존됩니다.\n"
        " 이 API는 인증이 필요하지 않습니다. Mock API이므로 토큰 없이 테스트하세요."
    ),
    auth=[],
    responses={
        204: OpenApiResponse(description="삭제 성공 - 응답 본문 없음"),
        401: OpenApiResponse(description="인증 정보가 없거나 유효하지 않습니다."),
        403: OpenApiResponse(description="해당 리소스를 삭제할 권한이 없습니다."),
        404: OpenApiResponse(description="Test not found."),
    },
)
# (admin) 쪽지시험 삭제
class AdminTestDeleteAPIView(APIView):
    # 실제 구현시 관리자 권한 부여
    permission_classes = [AllowAny]

    def delete(self, request: Request, test_id: int) -> Response:
        # mock: 존재하지 않는 시험 예외 처리
        if test_id == 9999:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # 정상 삭제 응답 (실제 삭제 로직 없이 204 응답만)
        return Response(status=status.HTTP_204_NO_CONTENT)


# (admin)쪽지시험 수정
@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 수정 API",
    description=" 이 API는 인증이 필요하지 않습니다. Mock API이므로 토큰 없이 테스트하세요.",
    auth=[],
)
class AdminTestUpdateAPIView(APIView):
    permission_classes = [AllowAny]  # 추후 IsAuthenticated + 권한 검사로 변경 예정
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = AdminTestUpdateSerializer

    def patch(self, request: Request, test_id: int) -> Response:
        # mock: 존재하지 않는 시험 예외 처리
        if test_id == 9999:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # mock subject 객체
        subject = Subject(id=validated_data.get("subject_id", 1), title="컴퓨터공학")

        # mock test 객체 (실제 서비스라면 DB 조회로 교체 필요)
        test = Test(
            id=test_id,
            title="기존 제목",
            subject=subject,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        test.subject_id = subject.id

        # 수정 반영
        updated_test = serializer.update(test, validated_data)

        # 응답
        response_serializer = self.serializer_class(instance=updated_test)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


# (admin)쪽지시험 상세조회
@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 상세조회 API",
    description=" 이 API는 인증이 필요하지 않습니다. Mock API이므로 토큰 없이 테스트하세요.",
    auth=[],
)
class AdminTestDetailAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TestDetailSerializer

    def get(self, request: Request, test_id: int) -> Response:
        # mock: 존재하지 않는 시험 예외 처리
        if test_id == 9999:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        subject = Subject(id=1, title="컴퓨터공학")

        questions = [
            TestQuestion(
                id=101,
                type="multiple_choice",
                question="스택의 LIFO는 무엇의 약자인가요?",
                point=5,
            ),
            TestQuestion(
                id=102,
                type="blank",
                question="다음 문장을 완성하세요",
                point=5,
            ),
        ]

        # mock 문제에 상세 필드 추가
        questions_data = TestQuestionSimpleSerializer(questions, many=True).data

        # detail 필드를 응답 dict에 수동으로 추가
        questions_data[0]["prompt"] = None
        questions_data[0]["options"] = ["Last In", "First Out"]
        questions_data[0]["answer"] = "Last In First Out"

        questions_data[1]["prompt"] = "자료구조에서 큐는 ____ 구조입니다."
        questions_data[1]["options"] = []
        questions_data[1]["answer"] = "FIFO"

        test = Test(
            id=test_id,
            title="자료구조 쪽지시험",
            subject=subject,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # 응답에 필요한 데이터 수동 조합
        data = self.serializer_class(test).data
        data["questions"] = questions_data
        data["question_count"] = len(questions)

        return Response(data, status=status.HTTP_200_OK)


# (admin)쪽지시험 목록조회
@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 목록조회 API",
    description=" 이 API는 인증이 필요하지 않습니다. Mock API이므로 토큰 없이 테스트하세요.",
    auth=[],
)
class AdminTestListView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TestListSerializer

    def get(self, request: Request) -> Response:
        subject = Subject(id=1, title="컴퓨터공학")

        test = Test(
            id=4, title="자료구조 쪽지시험", subject=subject, created_at=timezone.now(), updated_at=timezone.now()
        )

        # 수동 필드 주입
        test.question_count = 5  # type: ignore[attr-defined]
        test.submission_count = 20  # type: ignore[attr-defined]

        serializer = self.serializer_class(instance=[test], many=True)
        response_data = serializer.data

        # detail_url 필드 수동 추가
        for item in response_data:
            item["detail_url"] = f"/api/v1/admin/tests/{item['id']}/"

        return Response(
            {
                "count": len(response_data),
                "next": None,
                "previous": None,
                "results": response_data,
            },
            status=status.HTTP_200_OK,
        )


# (admin)쪽지시험 생성


@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 생성 API",
    description="JWT 인증이 필요하며, 관리자/스태프 권한을 가진 사용자만 접근할 수 있습니다.",
    request={"multipart/form-data": TestCreateSerializer},
)
class AdminTestCreateAPIView(APIView):
    serializer_class = TestCreateSerializer
    permission_classes = [IsAdminOrStaff]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request: Request) -> Response:

        if settings.DEBUG:
            # 개발환경에서만 request.user를 임의로 세팅
            request.user = User.objects.get(email="testadmin@example.com")
            # print("[INFO] 개발용 request.user 주입: testadmin@example.com")

        serializer = self.serializer_class(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # 1) 과목 유효성 검증
        try:
            subject = Subject.objects.get(id=validated_data["subject_id"])
        except Subject.DoesNotExist:
            return Response({"subject_id": ["해당 과목이 존재하지 않습니다."]}, status=status.HTTP_400_BAD_REQUEST)

        thumbnail_file = validated_data.pop("thumbnail_file")

        # 2) DB에 Test를 먼저 생성해 id 확보
        test = Test.objects.create(
            title=validated_data["title"],
            subject=subject,
            thumbnail_img_url="",  # 업로드 전이라 임시로 빈 값 저장
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # 3) S3 업로드 key에 test.id 포함 + 난수 추가

        random_str = uuid.uuid4().hex[:6]
        s3_key = f"oz_externship_be/tests/thumbnail_images/{test.id}_{random_str}.png"

        # settings의 AWS 키 값들은 Django 설정 특성상 mypy에서 Any로 추론되므로,
        # boto3.client()에 넘기기 전에 명확히 str로 타입 고정
        aws_access_key_id = cast(str, settings.AWS_ACCESS_KEY_ID)
        aws_secret_access_key = cast(str, settings.AWS_SECRET_ACCESS_KEY)
        aws_region = cast(str, settings.AWS_REGION)
        aws_bucket = cast(str, settings.AWS_STORAGE_BUCKET_NAME)

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region,
        )

        try:
            s3_client.upload_fileobj(
                thumbnail_file,
                aws_bucket,
                s3_key,
                ExtraArgs={"ContentType": thumbnail_file.content_type},  # ACL 없이 업로드된 객체라도 퍼블릭에 접근 가능
            )
            thumbnail_img_url = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{s3_key}"

        # 예외 처리
        except NoCredentialsError:
            return Response({"error": "AWS 자격증명이 누락되었습니다. AWS 키 설정을 확인하세요."}, status=500)

        # 4) 업로드 완료 후 Test에 실제 thumbnail_img_url 업데이트
        test.thumbnail_img_url = thumbnail_img_url
        test.save()

        # 5) 생성된 객체 직렬화하여 응답
        response_serializer = self.serializer_class(instance=test)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
