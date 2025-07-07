from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from apps.courses.views.course_views import (
    CourseDetailView,
    CourseListCreateView,
)
from apps.courses.views.dropdown_list_views import (
    GenerationDropdownListAPIView,  # 프론트 추가분
)
from apps.courses.views.dropdown_list_views import (
    CourseDropdownListAPIView,
)
from apps.courses.views.generation_views import (
    CourseTrendView,
    GenerationCreateView,
    GenerationDeleteView,
    GenerationDetailView,
    GenerationListView,
    GenerationUpdateView,
    MonthlyCourseView,
    OngoingCourseView,
)
from apps.courses.views.subject_views import (
    SubjectDetailAPIView,
    SubjectDropdownListAPIView,
    SubjectListCreateAPIView,
)

urlpatterns = [
    path("courses/", CourseListCreateView.as_view(), name="v1_admin_course_list"),
    path("courses/<int:course_id>/", CourseDetailView.as_view(), name="v1_admin_course_detail"),
    path("courses/dropdown-list/", CourseDropdownListAPIView.as_view(), name="admin-course-dropdown-list"),
    path("subjects/", SubjectListCreateAPIView.as_view(), name="subject-list-create"),
    path("subjects/<int:subject_id>/", SubjectDetailAPIView.as_view(), name="subject-detail"),
    path(
        "subjects/<int:course_id>/dropdown-list/",
        SubjectDropdownListAPIView.as_view(),
        name="admin-subject-dropdown-list",
    ),
    path("generations/", GenerationCreateView.as_view(), name="generation_add_create"),
    path("generations/<int:pk>/update/", GenerationUpdateView.as_view(), name="generation_update"),
    path("generations/<int:pk>/delete/", GenerationDeleteView.as_view(), name="generation_delete"),
    path("generations/<int:pk>/detail/", GenerationDetailView.as_view(), name="generation_update_detail"),
    path("generations/list/", GenerationListView.as_view(), name="generation_list"),
    path("generations/dashboard/trend", CourseTrendView.as_view(), name="generation_trend"),
    path("generations/dashboard/monthly", MonthlyCourseView.as_view(), name="generation_monthly"),
    path("generations/dashboard/ongoing", OngoingCourseView.as_view(), name="generation_ongoing"),
    path(
        "generations/<int:course_id>/dropdown-list/",
        GenerationDropdownListAPIView.as_view(),
        name="admin-generation-dropdown-list",
    ),
]
