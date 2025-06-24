from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime

mock_categories = {
    1: {
        "id": 1,
        "name": "공지사항",
        "status": True,
        "created_at": "2025-06-22T07:11:44Z",
        "updated_at": "2025-06-22T07:11:44Z"
    },
    2: {
        "id": 2,
        "name": "자유게시판",
        "status": False,
        "created_at": "2025-06-20T09:00:00Z",
        "updated_at": "2025-06-20T11:00:00Z"
    }
}
class CategoryDetailAPIView(APIView):
    def get(self, request, id):
        category = mock_categories.get(id)
        if category:
            return Response(category, status=status.HTTP_200_OK)
        return Response({"detail": "해당 카테고리를 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        category = mock_categories.get(id)
        if not category:
            return Response({"detail": "해당 카테고리를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        is_active = request.data.get("is_active")
        if "is_active" not in request.data or not isinstance(is_active, bool):
            return Response(
            {"detail": "Invalid request payload. 'is_active' must be a boolean."},
            status=status.HTTP_400_BAD_REQUEST
        )


    # ✅ 실제로 상태 및 시간 수정
        category["status"] = is_active
        category["updated_at"] = datetime.utcnow().isoformat() + "Z"

        return Response(category, status=status.HTTP_200_OK)


    def post(self, request):
        name = request.data.get("name")
        status_value = request.data.get("status")

        if name == "공지사항":  # 이미 존재하는 카테고리
            return Response({
                "detail": "이미 존재하는 카테고리 이름입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "id": 2,
            "name": name,
            "status": status_value,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }, status=status.HTTP_200_OK)

    def delete(self, request, id):
        category = mock_categories.get(id)
        if not category:
            return Response({"detail": "Invalid category ID."}, status=status.HTTP_400_BAD_REQUEST)

class CategoryListCreateAPIView(APIView):
    def get(self, request):
        return Response(list(mock_categories.values()), status=status.HTTP_200_OK)