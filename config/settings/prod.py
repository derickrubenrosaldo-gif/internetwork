"""Configuración de producción: seguridad, PostgreSQL, HTTPS.

Falla al arrancar si falta configuración crítica: nunca se arranca en
producción con la clave de ejemplo ni con ``ALLOWED_HOSTS = ["*"]``.
"""

from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

if not SECRET_KEY or SECRET_KEY == "cambiar-en-produccion":
    raise ImproperlyConfigured("Define SECRET_KEY en producción con un valor largo y aleatorio.")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ["*"]:
    raise ImproperlyConfigured(
        "Define ALLOWED_HOSTS con tus dominios reales (nunca '*') en producción."
    )
if not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured("Define CSRF_TRUSTED_ORIGINS (con esquema https://) en producción.")

# Cookies y HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
