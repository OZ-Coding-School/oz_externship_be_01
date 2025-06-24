from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

@extend_schema(
    request={"application/json": {"access_code": "abc123"}},
    responses={200: "쪽지시험 응시 시작 응답 예시"},
    description="쪽지시험 응시 시작 API (Mock)"
)


# 쪽지시험 응시 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_test_submission_start(request):
    access_code = request.data.get("access_code")

    # access_code가 없으면 400 에러
    if not access_code :
        return Response({"detail": "인증 정보가 없거나 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # access_code가 'abc123'이 아니면 400 에러
    if access_code !="abc123":
        return Response({"detail": "인증 정보가 없거나 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 임시 데이터 (목 API용)
    data = {
      "test_id": 4,
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
          "point": 5
        },
        {
          "question_id": 2,
          "type": "O/X",
          "question": "CSS는 프로그래밍 언어이다.",
          "options": ["O", "X"],
          "point": 5
        }
      ]
    }

    return Response(data, status=status.HTTP_200_OK)

# 쪽지시험 제출 API
@api_view(['POST'])
#@permission_classes(['IsAuthenticated'])
def post_test_submission_submit(request):
    return Response({"message": "응시 시작"}, status=200)

# 쪽지시험 결과조회 API
@api_view(['GET'])
def get_test_submission_result(request):
    return Response({"message": "결과 조회 완료"}, status=200)


