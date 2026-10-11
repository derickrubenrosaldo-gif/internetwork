"""Enlaces mágicos de acceso al panel de clientes.

Token firmado con ``django.core.signing``: caduca a los 15 minutos y se
invalida al primer uso mediante un nonce registrado en ``UsedLoginToken``.
Nunca se guarda un secreto en claro: el nonce es el único dato persistido
y solo sirve para marcar el token como consumido.
"""

import secrets

from django.conf import settings
from django.core import signing

from .models import UsedLoginToken

SALT = "core.panel.login"


def make_token(email):
    """Firma un token de acceso para el correo indicado."""
    payload = {"email": email, "nonce": secrets.token_urlsafe(16)}
    return signing.dumps(payload, salt=SALT)


def read_token(token):
    """Valida firma y caducidad. Devuelve ``(email, nonce)``.

    Lanza ``SignatureExpired`` si caducó y ``BadSignature`` si la firma
    no es válida.
    """
    payload = signing.loads(token, salt=SALT, max_age=getattr(settings, "PANEL_LINK_MAX_AGE", 900))
    return payload["email"], payload["nonce"]


def consume_token(nonce, email=""):
    """Marca el nonce como usado. Devuelve ``False`` si ya estaba usado."""
    _, created = UsedLoginToken.objects.get_or_create(nonce=nonce, defaults={"email": email})
    return created
