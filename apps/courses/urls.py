from django.urls import path

from .views.course_views import CourseDetailView, CourseListCreateView

urlpatterns = [
    path("", CourseListCreateView.as_view(), name="v1_admin_course_list"),
    path("<int:course_id>/", CourseDetailView.as_view(), name="v1_admin_course_detail"),
]
