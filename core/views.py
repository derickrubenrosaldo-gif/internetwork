"""Vistas: página principal, formulario de contacto, SEO (robots), errores."""

import csv
import json
import logging
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from .forms import LeadForm
from .models import Differentiator, Service, SiteConfig, StoryStep

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SiteConfig.get_solo()
        context.update(
            {
                "config": config,
                "services": Service.objects.filter(active=True),
                "story_steps": StoryStep.objects.all(),
                "differentiators": Differentiator.objects.all(),
                "form": LeadForm(),
                "title": "INTERNETWORK | Conectando tu mundo",
                "meta_description": (
                    "INTERNETWORK: internet dedicado, conectividad en zonas rurales, "
                    "soluciones IT, infraestructura, desarrollo de software y páginas web."
                ),
                "canonical": self.request.build_absolute_uri("/"),
                "config_jsonld": json.dumps(self._jsonld(config), ensure_ascii=False).replace(
                    "<", "\\u003C"
                ),
            }
        )
        return context

    @staticmethod
    def _jsonld(config):
        return {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "additionalType": "https://schema.org/TelecommunicationsCompany",
            "name": "INTERNETWORK",
            "description": (
                "Internet dedicado, conectividad en zonas rurales, soluciones IT, "
                "infraestructura, desarrollo de software y páginas web."
            ),
            "email": config.email,
            "telephone": config.phone,
            "address": {"@type": "PostalAddress", "streetAddress": config.address},
            "areaServed": config.zones_list,
        }


def submit_lead(request):
    """Recepción del formulario de contacto (fetch + JSON)."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)

    # Honeypot: si un bot rellena el campo oculto, respondemos "éxito" sin guardar.
    if request.POST.get("honeypot"):
        return JsonResponse({"status": "ok", "message": "Gracias, nos pondremos en contacto."})

    ip = request.META.get("REMOTE_ADDR", "")

    # Rate limiting por IP con caché
    cache_key = f"lead_rate:{ip}"
    attempts = cache.get(cache_key, 0)
    if attempts >= settings.RATE_LIMIT_REQUESTS:
        return JsonResponse(
            {
                "status": "error",
                "message": "Demasiadas solicitudes. Intenta de nuevo en unos minutos.",
            },
            status=429,
        )
    cache.set(cache_key, attempts + 1, settings.RATE_LIMIT_SECONDS)

    form = LeadForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {"status": "error", "message": "Revisa los campos marcados.", "errors": form.errors},
            status=400,
        )

    lead = form.save(commit=False)
    lead.ip_address = ip
    lead.save()

    # Notificación por correo al equipo (no bloquea si el correo no está configurado)
    if settings.CONTACT_EMAIL:
        try:
            subject = f"Nueva solicitud de {lead.name} — {lead.service_of_interest}"
            message = render_to_string(
                "email/lead_notification.txt", {"lead": lead, "whatsapp": settings.WHATSAPP_NUMBER}
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or settings.CONTACT_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
        except Exception:
            logger.exception("No se pudo enviar la notificación por correo del lead %s", lead.id)

    whatsapp_url = None
    if settings.WHATSAPP_NUMBER:
        text = "%n".join(
            quote(line)
            for line in [
                "Solicitud para INTERNETWORK",
                f"Nombre: {lead.name}",
                f"Empresa: {lead.company or 'No indicada'}",
                f"Correo: {lead.email}",
                f"Teléfono: {lead.phone or 'No indicado'}",
                f"Servicio: {lead.service_of_interest}",
                f"Proyecto: {lead.message or 'Sin detalles adicionales'}",
            ]
        )
        whatsapp_url = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={text}"

    return JsonResponse(
        {
            "status": "ok",
            "message": "Solicitud enviada. Nos pondremos en contacto contigo pronto.",
            "whatsapp_url": whatsapp_url,
        }
    )


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def page_not_found(request, exception=None):
    try:
        config = SiteConfig.get_solo()
    except Exception:  # noqa: BLE001
        config = None
    return render(request, "404.html", {"config": config}, status=404)


def server_error(request):
    return render(request, "500.html", status=500)


# Utilidad para el admin: exportación CSV de leads (reutilizada en core/admin.py)
def leads_to_csv(queryset):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="leads.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ["Fecha", "Nombre", "Empresa", "Correo", "Teléfono", "Servicio", "Estado", "IP"]
    )
    for lead in queryset:
        writer.writerow(
            [
                lead.created_at.isoformat(),
                lead.name,
                lead.company,
                lead.email,
                lead.phone,
                lead.service_of_interest,
                lead.get_status_display(),
                lead.ip_address or "",
            ]
        )
    return response
