"""Context processors: datos globales disponibles en todas las plantillas."""

from .models import LegalPage


def legal_pages(request):
    """Páginas legales activas para los enlaces del footer."""
    return {
        "legal_pages": LegalPage.objects.filter(active=True).order_by("order", "id")
    }
