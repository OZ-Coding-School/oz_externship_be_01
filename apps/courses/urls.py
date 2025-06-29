from django.urls import path

from apps.courses.views.subject_views import (
    SubjectDetailAPIView,
    SubjectListCreateAPIView,
)

from .views.course_views import CourseDetailView, CourseListCreateView

urlpatterns = [
    path("courses/", CourseListCreateView.as_view(), name="v1_admin_course_list"),
    path("courses/<int:course_id>/", CourseDetailView.as_view(), name="v1_admin_course_detail"),
    path("subjects/", SubjectListCreateAPIView.as_view(), name="subject-list-create"),
    path("subjects/<int:subject_id>/", SubjectDetailAPIView.as_view(), name="subject-detail"),
]
