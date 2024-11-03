import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .envファイルを読み込む
env = environ.Env()
env.read_env(os.path.join(os.path.dirname(BASE_DIR), ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-cdf37x+3%p2_38gdz&^f5o&14j%g8-1%^-zzkmf$t3x@=fncrw"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "clothes_shop",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "clothes_shop.middleware.request_log.LogRequestResponseMiddleware",
]

ROOT_URLCONF = "djangopj.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "djangopj.wsgi.application"

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "[{asctime}] {levelname} [{name}:{lineno}] {message}",
#             "style": "{",
#         },
#     },
#     "filters": {
#         "debug_only": {
#             "()": "clothes_shop.logging_filters.DebugOnlyFilter",
#         },
#         "info_only": {
#             "()": "clothes_shop.logging_filters.InfoOnlyFilter",
#         },
#         "warning_only": {
#             "()": "clothes_shop.logging_filters.WarningOnlyFilter",
#         },
#         "error_only": {
#             "()": "clothes_shop.logging_filters.ErrorOnlyFilter",
#         },
#         "critical_only": {
#             "()": "clothes_shop.logging_filters.CriticalOnlyFilter",
#         },
#     },
#     "handlers": {
#         "debug_file": {
#             "level": "DEBUG",
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "/django/logs/debug/debug.log",
#             "when": "D",
#             "interval": 1,
#             "backupCount": 30,
#             "formatter": "verbose",
#             "filters": ["debug_only"],
#         },
#         "info_file": {
#             "level": "INFO",
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "/django/logs/info/info.log",
#             "when": "D",
#             "interval": 1,
#             "backupCount": 30,
#             "formatter": "verbose",
#             "filters": ["info_only"],
#         },
#         "warning_file": {
#             "level": "WARNING",
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "/django/logs/warning/warning.log",
#             "when": "D",
#             "interval": 1,
#             "backupCount": 30,
#             "formatter": "verbose",
#             "filters": ["warning_only"],
#         },
#         "error_file": {
#             "level": "ERROR",
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "/django/logs/error/error.log",
#             "when": "D",
#             "interval": 1,
#             "backupCount": 30,
#             "formatter": "verbose",
#             "filters": ["error_only"],
#         },
#         "critical_file": {
#             "level": "CRITICAL",
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "/django/logs/critical/critical.log",
#             "when": "D",
#             "interval": 1,
#             "backupCount": 30,
#             "formatter": "verbose",
#             "filters": ["critical_only"],
#         },
#     },
#     "loggers": {
#         "": {
#             "handlers": ["debug_file", "info_file", "warning_file", "error_file", "critical_file"],
#             "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
#         },
#     },
# }


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env("MYSQL_ENGINE"),
        "NAME": env("MYSQL_DB_NAME"),
        "USER": env("MYSQL_APP_USER"),
        "PASSWORD": env("MYSQL_APP_USER_PASSWORD"),
        "HOST": env("MYSQL_HOST"),
        "PORT": env("MYSQL_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = True

# REST Framework settings
REST_FRAMEWORK = {
    "COERCE_DECIMAL_TO_STRING": False,
}
