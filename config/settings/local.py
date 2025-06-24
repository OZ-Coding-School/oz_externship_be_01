from config.settings.base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = [
    "127.0.0.1",
]
