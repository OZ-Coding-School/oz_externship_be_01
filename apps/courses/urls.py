# apps/courses/urls.py

from django.urls import path

from apps.courses.views.subject_views import (
    SubjectDetailAPIView,
    SubjectListCreateAPIView,
)

# from rest_framework import routers

# router = routers.DefaultRouter(trailing_slash=False)
# router.register(r"api/v1/admin")

urlpatterns = [
    path("", SubjectListCreateAPIView.as_view(), name="subject-list-create"),
    path("<int:subject_id>/", SubjectDetailAPIView.as_view(), name="subject-detail"),
]
