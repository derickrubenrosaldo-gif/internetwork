"""Cabeceras de seguridad del sitio (sin dependencias externas).

El sitio solo carga recursos propios (JS/CSS compilados, fuentes
auto-hospedadas con fontsource, Lottie propio), así que no necesita
orígenes externos en la política de contenido.
"""


class SecurityHeadersMiddleware:
    """Añade Content-Security-Policy, Referrer-Policy y Permissions-Policy."""

    CSP = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "object-src 'none'"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        headers = {
            "Content-Security-Policy": self.CSP,
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
        }
        for name, value in headers.items():
            if name not in response:
                response[name] = value
        return response
