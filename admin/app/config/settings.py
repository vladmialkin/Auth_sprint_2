"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from split_settings.tools import include

include(
    "components/base.py",
    "components/apps.py",
    "components/middlewares.py",
    "components/debug_toolbar.py",
    "components/csrf.py",
    "components/templates.py",
    "components/database.py",
    "components/auth_validators.py",
    "components/logging.py",
    "components/drf.py",
    "components/redis.py",
    "components/constance.py",
    "components/auth_service.py",
)
