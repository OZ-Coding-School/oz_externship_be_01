from django.conf import settings
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("api/v1/qna/", include("apps.qna.urls")),
    path("api/v1/community/", include("apps.community.urls")),
    path("api/v1/admin/course/", include("apps.courses.urls")),
    path("api/v1/", include("apps.users.urls")),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    if "drf_spectacular" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
            path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
            path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

        ]


urlpatterns += [path("api/v1/", include("apps.tests.urls", namespace="tests"))]
