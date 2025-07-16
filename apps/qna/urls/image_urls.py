from django.urls import path

from apps.qna.views.image_views import ImageDeleteAPIView, ImageUploadAPIView

urlpatterns = [
    # image
    path("images/upload/", ImageUploadAPIView.as_view()),
    path("images/delete/", ImageDeleteAPIView.as_view()),
]
