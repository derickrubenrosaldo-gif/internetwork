"""Vistas: página principal, formulario de contacto, SEO (robots), errores."""

import csv
import json
import logging
import secrets
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import TemplateView

from .forms import LeadForm, PaymentForm
from .models import (
    Differentiator,
    LegalPage,
    Payment,
    Plan,
    Service,
    SiteConfig,
    StoryStep,
)

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
                "plans": Plan.objects.filter(active=True),
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


def legal_page(request, slug):
    """Páginas legales: aviso de privacidad, términos, aviso legal, cookies."""
    page = get_object_or_404(LegalPage, slug=slug, active=True)
    return render(
        request,
        "legal.html",
        {
            "page": page,
            "config": SiteConfig.get_solo(),
            "title": f"{page.title} | INTERNETWORK",
            "meta_description": page.content[:155],
            "canonical": request.build_absolute_uri(page.get_absolute_url()),
        },
    )


def payments_page(request):
    """Página de pagos: métodos y formulario de registro."""
    config = SiteConfig.get_solo()
    return render(
        request,
        "payments.html",
        {
            "config": config,
            "form": PaymentForm(),
            "title": "Pagos | INTERNETWORK",
            "meta_description": (
                "Realiza el pago de tus servicios INTERNETWORK: "
                "transferencia bancaria, tarjeta o efectivo."
            ),
            "canonical": request.build_absolute_uri("/pagos/"),
        },
    )


def submit_payment(request):
    """Recepción del formulario de pagos (fetch + JSON)."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)

    # Honeypot: si un bot rellena el campo oculto, respondemos "éxito" sin guardar.
    if request.POST.get("honeypot"):
        return JsonResponse({"status": "ok", "message": "Gracias."})

    ip = request.META.get("REMOTE_ADDR", "")

    # Rate limiting por IP con caché
    cache_key = f"payment_rate:{ip}"
    attempts = cache.get(cache_key, 0)
    if attempts >= settings.RATE_LIMIT_REQUESTS:
        return JsonResponse(
            {"status": "error", "message": "Demasiados intentos. Intenta de nuevo en unos minutos."},
            status=429,
        )
    cache.set(cache_key, attempts + 1, settings.RATE_LIMIT_SECONDS)

    form = PaymentForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {"status": "error", "message": "Revisa los campos marcados.", "errors": form.errors},
            status=400,
        )

    payment = form.save(commit=False)
    payment.ip_address = ip
    payment.reference = _new_reference()
    payment.save()

    return JsonResponse(
        {
            "status": "ok",
            "message": "Pago registrado. Usa tu referencia al transferir.",
            "reference": payment.reference,
            "instructions": SiteConfig.get_solo().payment_instructions,
        }
    )


def _new_reference():
    """Referencia única de pago: INT-AAAAMMDD-XXXX."""
    today = timezone.now().strftime("%Y%m%d")
    for _ in range(5):
        reference = f"INT-{today}-{secrets.token_hex(2).upper()}"
        if not Payment.objects.filter(reference=reference).exists():
            return reference
    return f"INT-{today}-{secrets.token_hex(6).upper()}"


def payments_to_csv(queryset):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="pagos.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Fecha",
            "Referencia",
            "Nombre",
            "Correo",
            "Teléfono",
            "Servicio o plan",
            "Monto",
            "Método",
            "Estado",
            "IP",
        ]
    )
    for payment in queryset:
        writer.writerow(
            [
                payment.created_at.isoformat(),
                payment.reference,
                payment.name,
                payment.email,
                payment.phone,
                payment.service,
                payment.amount,
                payment.get_method_display(),
                payment.get_status_display(),
                payment.ip_address or "",
            ]
        )
    return response


def client_panel(request):
    """Panel de clientes: consulta de pagos con correo + referencia."""
    config = SiteConfig.get_solo()
    email = request.session.get("client_email")
    if not email:
        return render(
            request,
            "panel_login.html",
            {
                "config": config,
                "title": "Panel de clientes | INTERNETWORK",
                "meta_description": "Consulta el estado de tus pagos y servicios.",
                "canonical": request.build_absolute_uri("/panel/"),
            },
        )
    payments = Payment.objects.filter(email__iexact=email).order_by("-created_at")
    paid = payments.filter(status="paid")
    pending = payments.filter(status="pending")
    return render(
        request,
        "panel.html",
        {
            "config": config,
            "payments": payments,
            "email": email,
            "total_paid": sum(p.amount for p in paid),
            "total_pending": sum(p.amount for p in pending),
            "title": "Mi panel | INTERNETWORK",
            "meta_description": "Consulta el estado de tus pagos y servicios.",
            "canonical": request.build_absolute_uri("/panel/"),
        },
    )


def client_login(request):
    """Acceso al panel de clientes (correo + referencia de pago)."""
    if request.method != "POST":
        return redirect("core:client_panel")
    email = request.POST.get("email", "").strip().lower()
    reference = request.POST.get("reference", "").strip().upper()
    if Payment.objects.filter(email__iexact=email, reference__iexact=reference).exists():
        request.session["client_email"] = email
        return redirect("core:client_panel")
    return render(
        request,
        "panel_login.html",
        {
            "config": SiteConfig.get_solo(),
            "error": "No encontramos ese pago. Revisa tu correo y tu referencia.",
            "title": "Panel de clientes | INTERNETWORK",
            "meta_description": "Consulta el estado de tus pagos y servicios.",
            "canonical": request.build_absolute_uri("/panel/"),
        },
    )


def client_logout(request):
    """Cerrar sesión del panel de clientes."""
    request.session.pop("client_email", None)
    return redirect("core:client_panel")


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
