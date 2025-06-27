from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class AdminDetailWithDrawalSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    reason = serializers.CharField(read_only=True)
    reason_detail = serializers.CharField(read_only=True)
    due_date = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
