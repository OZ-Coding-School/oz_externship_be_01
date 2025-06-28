from types import SimpleNamespace
from typing import List

from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers.post_pagination_serializers import AdminPostPaginationSerializer
from apps.community.serializers.post_serializers import PostDetailSerializer, PostUpdateSerializer
from urllib.parse import urlencode

# Mock data
mock_post_cache = []
def init_mock_posts(total=30) -> List[SimpleNamespace]:
    mock_post_cache.clear()
    for i in range(1, total + 1):
        is_notice = (i == 1)
        is_visible = (i != 2)
        category_id = i % 5 + 1

        auth_id = i + 1
        author = SimpleNamespace(
            id=auth_id,
            pk=auth_id,
            nickname=f'user_{auth_id}',
            profile_image_url=f'https://cdn.example.com/user_{auth_id}.jpg'
        )

        comments = [{
            "id": i,
            "author": {
                "id": i + 1,
                "nickname": "jjang_admin",
                "profile_image_url": "https://example.com/profile.jpg"
            },
            "content": f"@zizon_admin 댓글입니다.{i}",
            "created_at": "2025-06-20T13:00:00Z",
            "tagged_users": [
                {
                    "id": 1,
                    "nickname": "zizon_admin",
                    "profile_image_url": "https://example.com/profile.jpg"
                }
            ]
        }]

        post_dict = {
            'id': i,
            'pk': i,
            'category': {'id': category_id, 'name': f'카테고리 {category_id}'},
            'author': author,
            'title': f'게시글 제목 {i}',
            'content': f'게시글 내용입니다. ID: {i}',
            'view_count': i * 5,
            'likes_count': i % 3,
            'attachments': [
                {
                    "id": i,
                    "file_url": "https://example.com/file.pdf",
                    "file_name": "example.pdf"
                }
            ],
            'images': [
                {
                    "id": i,
                    "image_url": "https://example.com/image.jpg",
                    "image_name": "example.jpg"
                }
            ],
            'comment_count': len(comments),
            'comments': comments,
            'is_notice': is_notice,
            'is_visible': is_visible,
            'created_at': f"2025-06-{(i % 28) + 1:02d}T00:00:00Z",
            'updated_at': f"2025-06-{(i % 28) + 1:02d}T00:00:00Z",
        }

        mock_post_cache.append(SimpleNamespace(**post_dict))


#  캐시가 없으면 초기화
def mock_posts(total=30) -> List[SimpleNamespace]:
    if not mock_post_cache:
        init_mock_posts(total)
    return mock_post_cache

# ID 기반으로 전체 포스트 정보 반환
def get_post_by_id(post_id: int) -> SimpleNamespace:
    if not mock_post_cache:
        init_mock_posts()

    for post in mock_post_cache:
        if post.id == post_id:
            return post
    raise Http404(f"{post_id}번 게시글이 존재하지 않습니다.")

# 어드민 게시글 목록 조회
class AdminPostListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='admin 게시글 목록 조회',
        description='사용자 화면용 게시글 목록을 조건 없이 mock 데이터로 반환합니다.',
        responses={200: AdminPostPaginationSerializer},
        tags=['Community - 게시글'],
        parameters=[
            OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='페이지 번호'),
            OpenApiParameter(name='size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='페이지 크기'),
            OpenApiParameter(name='is_visible', type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, description='노출 여부'),
            OpenApiParameter(name='category_id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='카테고리 ID'),
            OpenApiParameter(name='ordering', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description='정렬 필드 (created_at, view_count, likes_count)'),
        ]
    )
    def get(self, request: Request) -> Response:
        page = max(int(request.query_params.get('page', 1)), 1)
        size = min(int(request.query_params.get('size', 10)), 100)
        is_visible_param = request.query_params.get('is_visible')
        category_id_param = request.query_params.get('category_id')
        ordering_param = request.query_params.get('ordering')

        posts = mock_posts()

        if is_visible_param is not None:
            is_visible = is_visible_param.lower() == 'true'
            posts = [p for p in posts if p.is_visible == is_visible]

        if category_id_param is not None:
            try:
                category_id = int(category_id_param)
                posts = [p for p in posts if p.category['id'] == category_id]
            except ValueError:
                pass

        if ordering_param in ('created_at', 'view_count', 'likes_count'):
            reverse = True
            posts.sort(key=lambda p: getattr(p, ordering_param), reverse=reverse)

        total = len(posts)
        start = (page - 1) * size
        end = start + size
        current_page_posts = posts[start:end]

        base_url = request.build_absolute_uri(request.path)
        query_params = request.query_params.copy()

        query_params['size'] = size
        query_params['page'] = page + 1
        next_url = f'{base_url}?{urlencode(query_params)}' if end < total else None

        query_params['page'] = page - 1
        prev_url = f'{base_url}?{urlencode(query_params)}' if page > 1 else None

        payload = {
            'count': total,
            'next': next_url,
            'previous': prev_url,
            'results': current_page_posts,
        }
        serializer = AdminPostPaginationSerializer(instance=payload)
        return Response(serializer.data)

# 어드민 게시글 상세 조회
class AdminPostDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='admin 게시글 상세 조회',
        description='관리자 페이지에서 게시글 상세 정보를 mock 데이터로 반환합니다.',
        responses={
            200: PostDetailSerializer,
            404: OpenApiResponse(description="존재하지 않는 게시글입니다."),
        },
        tags=['Community - 게시글'],
    )
    def get(self, request: Request, post_id: int) -> Response:
        post = get_post_by_id(post_id)
        serializer = PostDetailSerializer(instance=post)
        return Response(serializer.data)

# 어드민 게시글 수정
class AdminPostUpdateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="admin 게시글 수정",
        description="관리자 페이지에서 게시글 정보를 수정하는 mock API입니다. 실제 저장은 되지 않습니다.",
        request=PostUpdateSerializer,
        responses={
            200: PostDetailSerializer,
            404: OpenApiResponse(description="존재하지 않는 게시글입니다."),
        },
        tags=["Community - 게시글"],
    )
    def patch(self, request: Request, post_id: int) -> Response:
        serializer = PostUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        original_post = get_post_by_id(post_id)
        original_category_id = original_post.category["id"]
        category_id = validated.get("category", original_category_id)

        mock_response = {
            "id": post_id,
            "category": {
                "id": category_id,
                "name": "공지사항" if category_id == 1 else f"카테고리 {category_id}"
            },
            "author": original_post.author,
            "title": validated.get("title", original_post.title),
            "content": validated.get("content", original_post.content),
            "view_count": original_post.view_count,
            "likes_count": original_post.likes_count,
            "comment_count": original_post.comment_count,
            "is_visible": validated.get("is_visible", original_post.is_visible),
            "is_notice": original_post.is_notice,
            "attachments": validated.get("attachments", original_post.attachments),
            "images": original_post.images,
            "comments": original_post.comments,
            "created_at": original_post.created_at,
            "updated_at": "2025-06-27T15:00:00Z",
        }

        for idx, post in enumerate(mock_post_cache):
            if post.id == post_id:
                mock_post_cache[idx] = SimpleNamespace(**mock_response)
                break

        return Response(PostDetailSerializer(instance=SimpleNamespace(**mock_response)).data)

# 게시글 삭제
class AdminPostDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="admin 게시글 삭제",
        description="관리자 페이지에서 게시글을 삭제하는 mock API입니다.",
        responses={
            200: OpenApiResponse(description="게시글이 삭제되었습니다."),
            404: OpenApiResponse(description="존재하지 않는 게시글입니다."),
        },
        tags=["Community - 게시글"],
    )
    def delete(self, request: Request, post_id: int) -> Response:
        global mock_post_cache
        _ = get_post_by_id(post_id)  # 없으면 Http404 발생

        mock_post_cache = [p for p in mock_post_cache if p.id != post_id]
        return Response({"detail": "게시글이 삭제되었습니다."}, status=200)

# 게시글 노출 on/off
class AdminPostVisibilityToggleView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="admin 게시글 노출 상태 토글",
        description="관리자 페이지에서 게시글의 노출 상태를 on/off로 변경하는 mock API입니다.",
        responses={
            200: OpenApiResponse(description="게시글 노출 상태가 변경되었습니다."),
            404: OpenApiResponse(description="존재하지 않는 게시글입니다."),
        },
        tags=["Community - 게시글"],
    )
    def patch(self, request, post_id: int) -> Response:
        post = get_post_by_id(post_id)  # 없으면 Http404 발생

        new_is_visible = not post.is_visible
        post.is_visible = new_is_visible

        for idx, p in enumerate(mock_post_cache):
            if p.id == post_id:
                mock_post_cache[idx] = post
                break

        return Response({
            "id": post.id,
            "is_visible": post.is_visible,
            "message": f"게시글 노출 상태가 {'ON' if post.is_visible else 'OFF'}으로 변경되었습니다."
        }, status=status.HTTP_200_OK)