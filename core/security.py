"""Utilidades de seguridad: IP real, rate limiting atómico y CSV seguro."""

from functools import wraps

from django.conf import settings
from django.core.cache import cache

# Prefijos que una hoja de cálculo interpreta como fórmula (CSV injection).
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def noindex(view):
    """Añade ``X-Robots-Tag: noindex`` a la respuesta (zonas privadas)."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        response["X-Robots-Tag"] = "noindex, nofollow"
        return response

    return wrapper


def get_client_ip(request):
    """Devuelve la IP real del cliente.

    Detrás de N proxies de confianza, la IP del cliente es la enésima
    contada desde la derecha en ``X-Forwarded-For``: los saltos añadidos
    por un cliente no pueden falsificar ese valor. Sin proxies
    (``TRUSTED_PROXY_COUNT = 0``) se usa ``REMOTE_ADDR``, que no es
    manipulable desde fuera.
    """
    trusted = getattr(settings, "TRUSTED_PROXY_COUNT", 0)
    if trusted > 0:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        chain = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
        if len(chain) >= trusted:
            return chain[-trusted]
    return request.META.get("REMOTE_ADDR", "") or ""


def rate_limit(key, limit, window):
    """Rate limit atómico sobre caché.

    Devuelve ``True`` si la petición se permite. ``cache.add`` crea el
    contador de forma atómica (``incr`` no crea claves) y ``cache.incr``
    lo incrementa sin leer-y-escribir, así que dos peticiones simultáneas
    no pueden colarse contando el mismo valor.
    """
    cache_key = f"rl:{key}"
    if cache.add(cache_key, 1, window):
        return True
    try:
        count = cache.incr(cache_key)
    except ValueError:
        # La clave caducó entre add e incr: se recrea la ventana.
        cache.set(cache_key, 1, window)
        return True
    return count <= limit


def csv_safe(value):
    """Neutraliza fórmulas al exportar CSV (CSV injection).

    Un valor que empiece por ``= + - @`` (o tabulador/CR) se prefija con
    un apóstrofo para que la hoja de cálculo lo trate como texto.
    """
    text = "" if value is None else str(value)
    if text.startswith(_FORMULA_PREFIXES):
        return "'" + text
    return text
