"""Context processors: datos globales disponibles en todas las plantillas."""

from django.conf import settings
from django.urls import reverse

from .models import LegalPage

PRIVACY_SLUG = "aviso-de-privacidad"


def legal_pages(request):
    """Páginas legales activas para el footer y datos del aviso de privacidad."""
    pages = list(LegalPage.objects.filter(active=True).order_by("order", "id"))
    privacy = next((p for p in pages if p.slug == PRIVACY_SLUG), None)
    return {
        "legal_pages": pages,
        "privacy_notice_version": settings.PRIVACY_NOTICE_VERSION,
        "privacy_url": reverse("core:legal_page", kwargs={"slug": privacy.slug}) if privacy else "",
    }
