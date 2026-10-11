"""Configuración de desarrollo: DEBUG activo y SQLite."""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# El correo se imprime en consola: permite probar el enlace mágico sin SMTP.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Sin manifest en desarrollo para no requerir collectstatic
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
