from config.settings.base import *
from decouple import Config, RepositoryEnv
import os

DEBUG = True

env_path = os.path.join(BASE_DIR, "envs/.local.env")
config = Config(repository=RepositoryEnv(env_path))

SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = [
    "127.0.0.1",
]