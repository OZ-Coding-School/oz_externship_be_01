from apps.community.serializers.base_pagination_serializers import (
    BasePaginationSerializer,
)
from apps.community.serializers.post_serializers import PostListSerializer


class AdminPostPaginationSerializer(BasePaginationSerializer):
    results = PostListSerializer(many=True)
