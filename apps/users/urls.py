from django.urls import path

from apps.users.views.withdrawal_views import UserDeleteView, UserRestoreView

urlpatterns = [
    path('mock/delete/', UserDeleteView.as_view()),
    path('mock/restore/', UserRestoreView.as_view()),
]
