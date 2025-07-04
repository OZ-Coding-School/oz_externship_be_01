from apps.qna.urls.admin_urls import urlpatterns as admin_urlpatterns
from apps.qna.urls.answer_urls import urlpatterns as answer_urlpatterns
from apps.qna.urls.question_urls import urlpatterns as question_urlpatterns

urlpatterns = admin_urlpatterns + answer_urlpatterns + question_urlpatterns
