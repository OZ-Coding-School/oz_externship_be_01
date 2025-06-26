from types import SimpleNamespace
from typing import List

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers.post_pagination_serializers import AdminPostPaginationSerializer


def mock_posts(total=30) -> List[SimpleNamespace]:
    posts = []
    for i in range(1, total + 1):
        is_notice = (i == 1)
        is_visible = (i != 2)

        cat_id = i % 5 + 1
        category = SimpleNamespace(id=cat_id, pk=cat_id, name=f'카테고리 {cat_id}')

        auth_id = i + 1
        author = SimpleNamespace(id=auth_id, pk=auth_id,
                                 nickname=f'user_{auth_id}',
                                 profile_image_url=f'https://cdn.example.com/user_{auth_id}.jpg')

        post_dict = {
            'id': i,
            'pk': i,
            'category': category,
            'author': author,
            'title': f'게시글 제목 {i}',
            'view_count': i * 5,
            'likes_count': i % 3,
            'comment_count': i % 1,
            'is_notice': is_notice,
            'is_visible': is_visible,
            'created_at': f"2025-06-{(i % 28) + 1:02d}T00:00:00Z",
        }
        posts.append(SimpleNamespace(**post_dict))
    return posts


class AdminPostListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='게시글 목록 조회',
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
        from urllib.parse import urlencode
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
