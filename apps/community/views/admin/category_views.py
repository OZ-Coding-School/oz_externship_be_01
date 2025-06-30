from datetime import datetime

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import PostCategory
from apps.community.serializers.category_serializers import (
    CategoryCreateRequestSerializer,
    CategoryCreateResponseSerializer,
    CategoryDetailResponseSerializer,
    CategoryStatusUpdateRequestSerializer,
    CategoryStatusUpdateResponseSerializer,
    CategoryUpdateResponseSerializer,
)

# 카테고리 게시판 상세 조회
mock_valid_ids = [1, 2, 3]

mock_data_by_id = {
    1: {"id": 1, "name": "공지사항", "status": True},
    2: {"id": 2, "name": "자유게시판", "status": True},
    3: {"id": 3, "name": "Q&A", "status": False},
}


class AdminCommunityCategoryDetailAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="커뮤니티 게시판 상세 조회",
        description="카테고리 ID로 커뮤니티 카테고리 상세정보를 조회합니다.",
    )
    def get(self, request: Request, category_id: int) -> Response:
        if category_id not in mock_valid_ids:
            return Response({"detail": "해당 카테고리를 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        data = mock_data_by_id[category_id]
        response = {
            **data,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        # post_category = PostCategory.objects.get(id=1)
        # serializer = CategoryDetailResponseSerializer(instance=post_category)
        # return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(response, status=status.HTTP_200_OK)

    # 카테고리 삭제 API뷰
    @extend_schema(
        tags=["[Admin-category]"],
        operation_id="admin_category_delete",
        summary="관리자 카테고리 삭제",
        description="1, 2, 3번 카테고리만 존재하는 것으로 간주하고 그 외 ID는 삭제 실패로 처리",
    )
    def delete(self, request: Request, category_id: int) -> Response:
        mock_existing_ids = range(1, 4)
        if category_id not in mock_existing_ids:
            return Response({"detail": "해당 카테고리가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


# 카테고리 생성
class AdminCommunityCategoryCreateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="커뮤니티 게시판 카테고리 생성",
        description="새로운 커뮤니티 카테고리를 생성합니다.",
        request=CategoryCreateRequestSerializer,
    )
    def post(self, request: Request) -> Response:
        serializer = CategoryCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": "카테고리 이름은 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)
        category_data = PostCategory(
            id=1,
            name=serializer.validated_data.get("name"),
            status=serializer.validated_data.get("status", True),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        rsp_serializer = CategoryCreateResponseSerializer(category_data)
        return Response(rsp_serializer.data, status=status.HTTP_201_CREATED)


# 게시판 on/off 상태변경
class AdminCommunityCategoryStatusUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="카테고리 상태 변경",
        request=inline_serializer(
            name="CategoryStatusUpdateRequest",
            fields={
                "name": serializers.CharField(),
                "status": serializers.BooleanField(),
            },
        ),
        responses={200},
    )
    def patch(self, request: Request, category_id: int) -> Response:
        data = {"name": request.data.get("name"), "status": request.data.get("status")}
        serializer = CategoryStatusUpdateResponseSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data, status=200)


# 카테고리 목록 조회
class AdminCategoryListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="카테고리 목록 조회",
        description="카테고리 목록을 조회합니다.",
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        if not mock_data_by_id:
            return Response({"detail": "조회한 카테고리가 존재하지 않습니다."}, status=status.HTTP_403_FORBIDDEN)
        return Response(list(mock_data_by_id.values()), status=status.HTTP_200_OK)

    # serializer = CategoryListResponseSerializer(instance=mock_data_by_id)
    # serializer.is_valid(raise_exception=True)
    # return Response(serializer.data, status=status.HTTP_200_OK)


# 커뮤니티 게시판 카테고리 수정
class AdminCommunityCategoryUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="커뮤니티 게시판 카테고리 수정",
        description="카테고리의 이름과 상태를 수정합니다.",
        request=CategoryCreateRequestSerializer,
        responses={200: CategoryUpdateResponseSerializer},
    )
    def patch(self, request: Request, category_id: int) -> Response:
        serializer = CategoryCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": "입력값이 유효하지 않습니다."}, status=400)

        # mock용 예시 객체 생성
        updated_category = PostCategory(
            id=category_id,
            name=serializer.validated_data.get("name"),
            status=serializer.validated_data.get("status"),
            updated_at=datetime.now(),
        )

        rsp_serializer = CategoryUpdateResponseSerializer(updated_category)
        return Response(rsp_serializer.data, status=200)
