# apps/qna/permissions.py
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models.user import User


class IsStaffPermission(permissions.BasePermission):
    """
    스태프 권한 (조교, 러닝 코치, 운영 매니저)
    TA, LC, OM 역할을 가진 사용자만 접근 가능
    """
    message = "스태프 권한이 필요합니다. (조교, 러닝 코치, 운영 매니저만 접근 가능)"

    def has_permission(self, request: Request, view: APIView) -> bool:
        # 인증된 사용자인지 확인
        if not request.user or not request.user.is_authenticated:
            return False

        # User 타입인지 확인
        if not isinstance(request.user, User):
            return False

        # 스태프 역할인지 확인
        staff_roles = [User.Role.TA, User.Role.LC, User.Role.OM]
        return request.user.role in staff_roles


class IsStudentPermission(permissions.BasePermission):
    """
    수강생 권한
    STUDENT 역할을 가진 사용자만 접근 가능
    """
    message = "수강생 권한이 필요합니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        # 인증된 사용자인지 확인
        if not request.user or not request.user.is_authenticated:
            return False

        # User 타입인지 확인
        if not isinstance(request.user, User):
            return False

        # 수강생 역할인지 확인
        return request.user.role == User.Role.STUDENT


class IsGeneralUserPermission(permissions.BasePermission):
    """
    모든 이용자 권한
    인증된 모든 사용자가 접근 가능 (GENERAL 포함)
    """
    message = "로그인이 필요합니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        # 인증된 사용자인지 확인
        if not request.user or not request.user.is_authenticated:
            return False

        # User 타입인지 확인
        if not isinstance(request.user, User):
            return False

        # 모든 역할 허용
        return True


class IsAdminPermission(permissions.BasePermission):
    """
    관리자 권한
    ADMIN 역할을 가진 사용자만 접근 가능
    """
    message = "관리자 권한이 필요합니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        # 인증된 사용자인지 확인
        if not request.user or not request.user.is_authenticated:
            return False

        # User 타입인지 확인
        if not isinstance(request.user, User):
            return False

        # 관리자 역할인지 확인
        return request.user.role == User.Role.ADMIN


# 조합 권한 클래스들
class IsStudentOrStaffPermission(permissions.BasePermission):
    """
    수강생 또는 스태프 권한
    답변 작성, 댓글 작성에 사용
    """
    message = "수강생 또는 스태프 권한이 필요합니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        # 인증된 사용자인지 확인
        if not request.user or not request.user.is_authenticated:
            return False

        # User 타입인지 확인
        if not isinstance(request.user, User):
            return False

        # 수강생 또는 스태프 역할인지 확인
        allowed_roles = [User.Role.STUDENT, User.Role.TA, User.Role.LC, User.Role.OM]
        return request.user.role in allowed_roles


class IsStudentOrStaffOrAdminPermission(permissions.BasePermission):
    """
    수강생, 스태프 또는 관리자 권한
    대부분의 QNA 기능에 사용
    """
    message = "답변 작성 권한이 없습니다. (수강생, 조교, 러닝 코치, 운영 매니저, 관리자만 가능)"

    def has_permission(self, request: Request, view: APIView) -> bool:
        # 인증된 사용자인지 확인
        if not request.user or not request.user.is_authenticated:
            return False

        # User 타입인지 확인
        if not isinstance(request.user, User):
            return False

        # 수강생, 스태프, 관리자 역할인지 확인
        allowed_roles = [User.Role.STUDENT, User.Role.TA, User.Role.LC, User.Role.OM, User.Role.ADMIN]
        return request.user.role in allowed_roles