import datetime

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
from apps.tests.serializers.admin_crud_serializers import (
    AdminTestUpdateSerializer,
    TestCreateSerializer,
    TestDetailSerializer,
    TestListSerializer,
    TestQuestionSimpleSerializer,
)


@extend_schema(
    tags=["Admin | Test CRUD"],
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
    tags=["Admin | Test CRUD"],
    summary="쪽지시험 수정 API",
    description=" 이 API는 인증이 필요하지 않습니다. Mock API이므로 토큰 없이 테스트하세요.",
    auth=[],
)
class AdminTestUpdateAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminTestUpdateSerializer

    def patch(self, request: Request, test_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # mock: 존재하지 않는 시험 예외 처리
        if test_id == 9999:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        validated_data = serializer.validated_data

        # mock subject
        subject = Subject(id=validated_data.get("subject_id", 1), title="컴퓨터공학")

        # mock test
        test = Test(
            id=test_id,
            title=validated_data.get("title", "기존 제목"),
            subject=subject,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # 수동 필드 주입
        test.subject_id = subject.id
        serializer = self.serializer_class(instance=test)
        return Response(serializer.data, status=status.HTTP_200_OK)


# (admin)쪽지시험 상세조회
@extend_schema(
    tags=["Admin | Test CRUD"],
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

        test = Test(
            id=test_id, title="자료구조 쪽지시험", subject=subject, created_at=timezone.now(), updated_at=timezone.now()
        )

        # 응답에 필요한 데이터 수동 조합
        data = self.serializer_class(test).data
        data["questions"] = TestQuestionSimpleSerializer(questions, many=True).data
        data["question_count"] = len(questions)

        return Response(data, status=status.HTTP_200_OK)


# (admin)쪽지시험 목록조회
@extend_schema(
    tags=["Admin | Test CRUD"],
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

        return Response(
            {"count": len(serializer.data), "next": None, "previous": None, "results": serializer.data},
            status=status.HTTP_200_OK,
        )


# (admin)쪽지시험 생성


@extend_schema(
    tags=["Admin | Test CRUD"],
    summary="쪽지시험 생성 API",
    description=" 이 API는 인증이 필요하지 않습니다. Mock API이므로 토큰 없이 테스트하세요.",
    auth=[],
    request={"multipart/form-data": TestCreateSerializer},
)
class AdminTestCreateAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = TestCreateSerializer

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # 실제 DB 저장 없이 mock 객체 생성 / mock값 지정이 안될때 return값이 api명세서와 다름
            subject_id = serializer.validated_data.get("subject_id")

            test = Test(
                id=3,
                title=serializer.validated_data.get("title"),
                subject_id=subject_id,
                thumbnail_img_url="https://oz.com/sample_thumbnail.jpg",
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            serializer = self.serializer_class(instance=test)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
