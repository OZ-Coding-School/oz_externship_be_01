from config.settings.base import *

DEBUG = True
ALLOWED_HOSTS: list[str] = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(" ")

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = [
    "127.0.0.1",
]

ALLOWED_ORIGINS: list[str] = os.getenv("CORS_ALLOWED_ORIGINS", "").split(" ")
CORS_ALLOWED_ORIGINS += ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS += ALLOWED_ORIGINS
