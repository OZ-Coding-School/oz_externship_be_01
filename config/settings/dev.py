from config.settings.base import *

DEBUG = False
ALLOWED_HOSTS: list[str] = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(" ")

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = [
    "127.0.0.1",
]
