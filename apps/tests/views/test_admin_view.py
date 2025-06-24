
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


# 쪽지시험 응시내역 목록 조회 API
@api_view(['GET'])
def admin_test_submissions(request):
    return Response({"message: 목록 조회 완료"}, status=200)

# 쪽지시험 응시내역 상세 조회 API
@api_view(['GET'])
def admin_test_submissions_detail(request):
    return Response({"message: 상세 조회 완료"}, status=200)

# 쪽지시험 응시내역 삭제 API
@api_view(['delete'])
def admin_test_submissions_delete(request):
    return Response({"message: 응시내역 삭제 완료"}, status=200)