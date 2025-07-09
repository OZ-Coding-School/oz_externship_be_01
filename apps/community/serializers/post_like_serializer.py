from rest_framework import serializers


class PostLikeResponseSerializer(serializers.Serializer):
    liked = serializers.BooleanField(help_text="좋아요 상태 (True: 추가됨, False: 취소됨)")
    like_count = serializers.IntegerField(help_text="게시글의 총 좋아요 수")
