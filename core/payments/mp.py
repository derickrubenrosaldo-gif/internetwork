"""Integración con Mercado Pago (Checkout Pro).

El sitio **nunca** recibe ni guarda datos de tarjeta: se crea una
preferencia en el servidor y el cliente paga en el checkout hospedado de
Mercado Pago. El webhook verifica la firma (``x-signature``) y luego
consulta el pago en la API para confirmarlo de forma idempotente.

Sin ``MP_ACCESS_TOKEN`` configurado, ``is_configured()`` es falso y la
página de pagos oculta Tarjeta y OXXO.
"""

import hashlib
import hmac
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

API_BASE = "https://api.mercadopago.com"
TIMEOUT = 10


def is_configured():
    """True si hay credenciales para operar con Mercado Pago."""
    return bool(getattr(settings, "MP_ACCESS_TOKEN", ""))


def create_preference(payment, request):
    """Crea una preferencia de pago y devuelve ``(init_point, preference_id)``.

    ``external_reference`` es la referencia del pago, que permite conciliar
    el webhook con nuestro registro.
    """
    if not is_configured():
        raise RuntimeError("Mercado Pago no está configurado.")

    base = request.build_absolute_uri("/")
    payload = {
        "items": [
            {
                "title": payment.service,
                "quantity": 1,
                "unit_price": float(payment.amount),
                "currency_id": "MXN",
            }
        ],
        "external_reference": payment.reference,
        "statement_descriptor": "INTERNETWORK",
        "back_urls": {
            "success": f"{base}pagos/?estado=gracias",
            "pending": f"{base}pagos/?estado=pendiente",
            "failure": f"{base}pagos/?estado=error",
        },
        "auto_return": "approved",
        "notification_url": request.build_absolute_uri("/pagos/webhook/mercadopago/"),
    }
    data = _request("POST", "/checkout/preferences", payload)
    return data.get("init_point") or data.get("sandbox_init_point"), str(data.get("id", ""))


def fetch_payment(payment_id):
    """Consulta un pago por su id en Mercado Pago."""
    return _request("GET", f"/v1/payments/{payment_id}", None)


def verify_signature(headers, data_id):
    """Valida la cabecera ``x-signature`` del webhook.

    Mercado Pago firma un manifiesto con HMAC-SHA256 usando el secreto
    del webhook. Devuelve ``True`` si la firma es válida (o si no hay
    secreto configurado: en ese caso el webhook no se acepta).
    """
    secret = getattr(settings, "MP_WEBHOOK_SECRET", "")
    if not secret:
        return False

    signature = headers.get("x-signature", "")
    request_id = headers.get("x-request-id", "")
    parts = dict(item.split("=", 1) for item in signature.split(",") if "=" in item)
    ts = parts.get("ts", "")
    received = parts.get("v1", "")
    if not ts or not received:
        return False

    manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received)


def _request(method, path, payload):
    """Llamada HTTP a la API de Mercado Pago (stdlib, sin dependencias)."""
    url = f"{API_BASE}{path}"
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=body, method=method)
    request.add_header("Authorization", f"Bearer {settings.MP_ACCESS_TOKEN}")
    request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        logger.warning("Mercado Pago %s %s → %s", method, path, exc.code)
        raise
    except urllib.error.URLError as exc:
        logger.warning("Mercado Pago %s %s → %s", method, path, exc.reason)
        raise
