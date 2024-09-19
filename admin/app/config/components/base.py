from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = env.str("ALLOWED_HOSTS").split(",")

BASE_URL = env.str("BASE_URL", "")
API_PREFIX = env.str("API_PREFIX", "api/v1/")

HOST = env.str("HOST", "http://localhost/")

ROOT_URLCONF = "config.urls"

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = ["movies/locale"]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = f"/{BASE_URL}static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = f"/{BASE_URL}media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

WSGI_APPLICATION = "config.wsgi.application"
