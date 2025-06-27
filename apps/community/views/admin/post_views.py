from types import SimpleNamespace
from typing import List

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers.post_pagination_serializers import AdminPostPaginationSerializer
from apps.community.serializers.post_serializers import PostDetailSerializer
from urllib.parse import urlencode

# 어드민 게시글 목록 조회 (Mock data)
def mock_posts(total=30) -> List[SimpleNamespace]:
    posts = []
    for i in range(1, total + 1):
        is_notice = (i == 1)
        is_visible = (i != 2)

        category_id = i % 5 + 1

        auth_id = i + 1
        author = SimpleNamespace(id=auth_id, pk=auth_id,
                                 nickname=f'user_{auth_id}',
                                 profile_image_url=f'https://cdn.example.com/user_{auth_id}.jpg')

        post_dict = {
            'id': i,
            'pk': i,
            'category': {'id': category_id, 'name': f'카테고리 {category_id}'},
            'author': author,
            'title': f'게시글 제목 {i}',
            'view_count': i * 5,
            'likes_count': i % 3,
            'comment_count': i % 1,
            'is_notice': is_notice,
            'is_visible': is_visible,
            'created_at': f"2025-06-{(i % 28) + 1:02d}T00:00:00Z",
            'updated_at': f"2025-06-{(i % 28) + 1:02d}T00:00:00Z",
        }
        posts.append(SimpleNamespace(**post_dict))
    return posts

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
        responses={200: PostDetailSerializer},
        tags=['Community - 게시글'],
    )
    def get(self, request: Request, post_id: int) -> Response:
        category_id = 1
        mock_data = {
            "id": post_id,
            "category": {"id": category_id, "name": f"카테고리 {category_id}"},
            "author": {
                "id": 1,
                "nickname": "zizon_admin",
                "profile_image_url": "https://example.com/profile.jpg"
            },
            "title": "관리자용 상세 게시글",
            "content": "이 게시글은 관리자 전용 조회입니다.",
            "view_count": 154,
            "likes_count": 12,
            "comment_count": 3,
            "is_visible": True,
            "is_notice": False,
            "attachments": [
                {
                    "id": 1,
                    "file_url": "https://example.com/file.pdf",
                    "file_name": "example.pdf"
                }
            ],
            "images": [
                {
                    "id": 1,
                    "file_url": "https://example.com/file.jpg",
                    "file_name": "example.jpg"
                }
            ],
            "comments": [
                {
                    "id": 201,
                    "author": {
                        "id": 2,
                        "nickname": "jjang_admin",
                    },
                    "content": "@zizon_admin 댓글입니다.",
                    "created_at": "2025-06-20T13:00:00Z",
                    "tagged_users": [
                        {
                            "id": 1,
                            "nickname": "zizon_admin",
                            "profile_image_url": "https://example.com/profile.jpg"
                        }
                    ]
                }
            ],
            "created_at": "2025-06-20T12:00:00Z",
            "updated_at": "2025-06-20T12:00:00Z"
        }

        serializer = PostDetailSerializer(instance=SimpleNamespace(**mock_data))
        return Response(serializer.data)