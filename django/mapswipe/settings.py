"""
Django settings for mapswipe project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
import sys
from pathlib import Path

import environ
from mapswipe import sentry

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(
    DJANGO_LOG_LEVEL=(str, "INFO"),  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    DJANGO_DEBUG=(bool, False),
    DJANGO_SECRET_KEY=str,
    DJANGO_ALLOWED_HOST=(list, ["*"]),
    DJANGO_DB_NAME=str,
    DJANGO_DB_USER=str,
    DJANGO_DB_PWD=str,
    DJANGO_DB_HOST=str,
    DJANGO_DB_PORT=int,
    DJANGO_CORS_ORIGIN_REGEX_WHITELIST=(list, []),
    # Static, Media configs
    DJANGO_STATIC_ROOT=(str, os.path.join(BASE_DIR, "assets/static")),  # Where to store
    DJANGO_MEDIA_ROOT=(str, os.path.join(BASE_DIR, "assets/media")),  # Where to store
    # Sentry
    SENTRY_DSN=(str, None),
    SENTRY_SAMPLE_RATE=(float, 0.2),
    # Misc
    RELEASE=(str, "develop"),
    MAPSWIPE_ENVIRONMENT=str,  # dev/prod
    APP_TYPE=str,
    # Testing
    PYTEST_XDIST_WORKER=(str, None),
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DJANGO_DEBUG")

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOST")
MAPSWIPE_ENVIRONMENT = env("MAPSWIPE_ENVIRONMENT")
APP_TYPE = env("APP_TYPE")


# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    # External apps
    "corsheaders",
    "strawberry.django",
    # Internal apps
    "apps.existing_database",
    "apps.aggregated",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mapswipe.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                # 'django.contrib.auth.context_processors.auth',
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mapswipe.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": env("DJANGO_DB_HOST"),
        "PORT": env("DJANGO_DB_PORT"),
        "NAME": env("DJANGO_DB_NAME"),
        "USER": env("DJANGO_DB_USER"),
        "PASSWORD": env("DJANGO_DB_PWD"),
        "OPTIONS": {"options": "-c search_path=public"},
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_ROOT = env("DJANGO_STATIC_ROOT")
STATIC_URL = "/static/"

MEDIA_ROOT = env("DJANGO_MEDIA_ROOT")
MEDIA_URL = "/media/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# CORS CONFIGS
if not env("DJANGO_CORS_ORIGIN_REGEX_WHITELIST"):
    CORS_ORIGIN_ALLOW_ALL = True
else:
    # Example ^https://[\w-]+\.mapswipe\.org$
    CORS_ORIGIN_REGEX_WHITELIST = env("DJANGO_CORS_ORIGIN_REGEX_WHITELIST")


CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"(^/api/.*$)|(^/media/.*$)|(^/graphql/$)"
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "sentry-trace",
)

# Sentry Config
SENTRY_DSN = env("SENTRY_DSN")
SENTRY_SAMPLE_RATE = env("SENTRY_SAMPLE_RATE")
SENTRY_ENABLED = False

if SENTRY_DSN:
    SENTRY_CONFIG = {
        "dsn": SENTRY_DSN,
        "send_default_pii": True,
        "release": env("RELEASE"),  # XXX: 'release': sentry.fetch_git_sha(BASE_DIR),
        "environment": MAPSWIPE_ENVIRONMENT,
        "debug": DEBUG,
        "tags": {
            "site": ",".join(set(ALLOWED_HOSTS)),
        },
    }
    sentry.init_sentry(
        app_type=APP_TYPE,
        **SENTRY_CONFIG,
    )
    SENTRY_ENABLED = True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": ("%(asctime)s: - %(levelname)s - %(name)s - %(message)s"),
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "//django-data/django.log",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": env("DJANGO_LOG_LEVEL"),
    },
    "loggers": {
        "django": {
            "level": env("DJANGO_LOG_LEVEL"),
        },
    },
}


# See if we are inside a test environment (pytest)
TESTING = (
    any(
        [
            arg in sys.argv
            for arg in [
                "test",
                "pytest",
                "/usr/local/bin/pytest",
                "py.test",
                "/usr/local/bin/py.test",
                "/usr/local/lib/python3.6/dist-packages/py/test.py",
            ]
            # Provided by pytest-xdist
        ]
    )
    or env("PYTEST_XDIST_WORKER") is not None
)

DEFAULT_PAGINATION_LIMIT = 50
MAX_PAGINATION_LIMIT = 500
