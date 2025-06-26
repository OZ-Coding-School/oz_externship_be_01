from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from apps.courses.views.generation_views import (GenerationCreateView,
                                                 GenerationUpdateView,
                                                 GenerationDeleteView,
                                                 GenerationDetailView,
                                                 GenerationListView,
                                                 GenerationTrendView,
                                                 MonthlygenerationView,
                                                 OngoingGenerationView)

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
    path('api/v1/admin/generations/', GenerationCreateView.as_view(), name='generation_add_create'),
    path('api/v1/admin/generations/<int:pk>/update/', GenerationUpdateView.as_view(), name='generation_update'),
    path('api/v1/admin/generations/<int:pk>/delete/', GenerationDeleteView.as_view(), name='generation_delete'),
    path('api/v1/admin/generations/<int:pk>/detail/', GenerationDetailView.as_view(), name='generation_update_detail'),
    path('api/v1/admin/generations/list/', GenerationListView.as_view(), name='generation_list'),
    path('api/v1/admin/generations/dashboard/trend', GenerationTrendView.as_view(), name='generation_trend'),
    path('api/v1/admin/generations/dashboard/Monthly', MonthlygenerationView.as_view(), name='generation_monthly'),
    path('api/v1/admin/generations/dashboard/ongoing', OngoingGenerationView.as_view(), name='generation_ongoing'),
]
