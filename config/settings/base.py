"""Configuración base compartida por desarrollo y producción."""

from decimal import Decimal
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Variables de entorno (django-environ) — ver .env.example
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    RATE_LIMIT_REQUESTS=(int, 5),
    RATE_LIMIT_SECONDS=(int, 60),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="cambiar-en-produccion")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# ---------------------------------------------------------------------------
# Aplicaciones y middleware
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.legal_pages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Base de datos: SQLite en desarrollo, PostgreSQL en producción (DATABASE_URL)
# ---------------------------------------------------------------------------
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}

# Caché (para rate limiting): memoria local por defecto, Redis si se define CACHE_URL
if env("CACHE_URL", default=None):
    CACHES = {"default": env.cache_url("CACHE_URL")}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estáticos (WhiteNoise)
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Configuración del negocio (contacto y anti-spam)
# ---------------------------------------------------------------------------
CONTACT_EMAIL = env("CONTACT_EMAIL", default="")
WHATSAPP_NUMBER = env("WHATSAPP_NUMBER", default="")

EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=CONTACT_EMAIL)

RATE_LIMIT_REQUESTS = env("RATE_LIMIT_REQUESTS")
RATE_LIMIT_SECONDS = env("RATE_LIMIT_SECONDS")

# ---------------------------------------------------------------------------
# Seguridad operativa
# ---------------------------------------------------------------------------
# Nº de proxies de confianza delante de la app (0 = usar REMOTE_ADDR).
TRUSTED_PROXY_COUNT = env.int("TRUSTED_PROXY_COUNT", default=0)

# Tope del monto que un cliente puede registrar en un pago.
PAYMENT_MAX_AMOUNT = Decimal(env("PAYMENT_MAX_AMOUNT", default="100000"))

# Enlaces mágicos del panel de clientes (caducidad y rate limit).
PANEL_LINK_MAX_AGE = env.int("PANEL_LINK_MAX_AGE", default=900)  # 15 minutos
PANEL_LINK_REQUESTS = env.int("PANEL_LINK_REQUESTS", default=3)
PANEL_LINK_SECONDS = env.int("PANEL_LINK_SECONDS", default=3600)

# Mercado Pago (opcional). Sin MP_ACCESS_TOKEN, tarjeta y OXXO quedan ocultos.
MP_ACCESS_TOKEN = env("MP_ACCESS_TOKEN", default="")
MP_PUBLIC_KEY = env("MP_PUBLIC_KEY", default="")
MP_WEBHOOK_SECRET = env("MP_WEBHOOK_SECRET", default="")

# Versión del aviso de privacidad aceptado en los formularios.
PRIVACY_NOTICE_VERSION = env("PRIVACY_NOTICE_VERSION", default="2026-10")
