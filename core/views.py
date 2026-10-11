"""Vistas: página principal, formularios, pagos, panel de clientes, SEO y errores."""

import csv
import json
import logging
import secrets
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
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
from .payments import mp
from .security import csv_safe, get_client_ip, noindex, rate_limit

logger = logging.getLogger(__name__)

# Alfabeto sin caracteres ambiguos (0/O, 1/I/L) para referencias legibles.
_REFERENCE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SiteConfig.get_solo()

        # ?plan=<slug> preselecciona el plan en el formulario de contacto.
        slug = self.request.GET.get("plan", "").strip()
        selected_plan = Plan.objects.filter(slug=slug, active=True).first() if slug else None
        initial = {}
        if selected_plan:
            speed = f" ({selected_plan.speed})" if selected_plan.speed else ""
            initial["message"] = f"Me interesa el plan {selected_plan.name}{speed}."

        context.update(
            {
                "config": config,
                "services": Service.objects.filter(active=True),
                "plans": Plan.objects.filter(active=True, price_amount__isnull=False),
                "selected_plan": selected_plan,
                "story_steps": StoryStep.objects.all(),
                "differentiators": Differentiator.objects.all(),
                "form": LeadForm(initial=initial),
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
            "areaServed": config.coverage_municipalities,
        }


def submit_lead(request):
    """Recepción del formulario de contacto (fetch + JSON)."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)

    # Honeypot: si un bot rellena el campo oculto, respondemos "éxito" sin guardar.
    if request.POST.get("honeypot"):
        return JsonResponse({"status": "ok", "message": "Gracias, nos pondremos en contacto."})

    ip = get_client_ip(request)
    if not rate_limit(f"lead:{ip}", settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_SECONDS):
        return JsonResponse(
            {
                "status": "error",
                "message": "Demasiadas solicitudes. Intenta de nuevo en unos minutos.",
            },
            status=429,
        )

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
        lines = [
            "Solicitud para INTERNETWORK",
            f"Nombre: {lead.name}",
            f"Empresa: {lead.company or 'No indicada'}",
            f"Correo: {lead.email}",
            f"Teléfono: {lead.phone or 'No indicado'}",
            f"Servicio: {lead.service_of_interest}",
            f"Proyecto: {lead.message or 'Sin detalles adicionales'}",
        ]
        text = "%0A".join(quote(line) for line in lines)
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


def payment_methods():
    """Métodos de pago disponibles.

    Tarjeta y OXXO requieren una pasarela configurada; sin ella solo se
    ofrece transferencia.
    """
    methods = [("transfer", Payment.METHOD_CHOICES[0][1])]
    if mp.is_configured():
        methods += list(Payment.METHOD_CHOICES[1:])
    return methods


def payments_page(request):
    """Página de pagos: métodos y formulario de registro."""
    config = SiteConfig.get_solo()
    methods = payment_methods()
    return render(
        request,
        "payments.html",
        {
            "config": config,
            "form": PaymentForm(methods=methods),
            "methods": methods,
            "gateway_ready": mp.is_configured(),
            "title": "Pagos | INTERNETWORK",
            "meta_description": (
                "Realiza el pago de tus servicios INTERNETWORK y obtén tu "
                "referencia para transferencia."
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

    ip = get_client_ip(request)
    if not rate_limit(f"payment:{ip}", settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_SECONDS):
        return JsonResponse(
            {
                "status": "error",
                "message": "Demasiados intentos. Intenta de nuevo en unos minutos.",
            },
            status=429,
        )

    form = PaymentForm(request.POST, methods=payment_methods())
    if not form.is_valid():
        return JsonResponse(
            {"status": "error", "message": "Revisa los campos marcados.", "errors": form.errors},
            status=400,
        )

    payment = form.save(commit=False)
    payment.ip_address = ip
    payment.reference = _new_reference()
    payment.save()

    # Métodos con pasarela: se crea el checkout hospedado y se redirige allí.
    if payment.method in ("card", "cash") and mp.is_configured():
        try:
            init_point, preference_id = mp.create_preference(payment, request)
        except Exception:
            logger.exception(
                "No se pudo crear la preferencia de Mercado Pago %s", payment.reference
            )
            payment.delete()
            return JsonResponse(
                {
                    "status": "error",
                    "message": "No pudimos abrir el pago con tarjeta. Intenta de nuevo.",
                },
                status=502,
            )
        payment.provider = "mercadopago"
        payment.provider_ref = preference_id
        payment.save(update_fields=["provider", "provider_ref"])
        return JsonResponse({"status": "ok", "checkout_url": init_point})

    return JsonResponse(
        {
            "status": "ok",
            "message": "Listo. Usa tu referencia al hacer la transferencia.",
            "reference": payment.reference,
            "instructions": SiteConfig.get_solo().payment_instructions,
        }
    )


def payment_webhook(request):
    """Webhook de Mercado Pago: verifica la firma y confirma el pago."""
    if request.method != "POST":
        return HttpResponse(status=405)

    data_id = request.GET.get("data.id") or request.GET.get("id") or ""
    if not data_id:
        try:
            body = json.loads(request.body or b"{}")
            data_id = str((body.get("data") or {}).get("id", ""))
        except ValueError:
            data_id = ""

    if not mp.verify_signature(request.headers, data_id):
        logger.warning("Webhook de Mercado Pago con firma inválida (data.id=%s)", data_id)
        return HttpResponse(status=401)

    try:
        remote = mp.fetch_payment(data_id)
    except Exception:
        logger.exception("No se pudo consultar el pago %s en Mercado Pago", data_id)
        return HttpResponse(status=502)

    reference = remote.get("external_reference")
    status = remote.get("status")
    if not reference:
        return HttpResponse(status=200)

    payment = Payment.objects.filter(reference=reference).first()
    if payment is None:
        return HttpResponse(status=200)

    # Idempotente: solo la primera confirmación cambia el estado.
    if status == "approved" and payment.status != "paid":
        payment.status = "paid"
        payment.paid_at = timezone.now()
        payment.provider = "mercadopago"
        payment.provider_ref = str(remote.get("id", ""))
        payment.save(update_fields=["status", "paid_at", "provider", "provider_ref"])

    return HttpResponse(status=200)


def _new_reference():
    """Referencia única de pago: INT-AAAAMMDD-<12 alfanuméricos>.

    Aleatoria y criptográficamente segura; nunca es una credencial.
    """
    today = timezone.now().strftime("%Y%m%d")
    for _ in range(5):
        suffix = "".join(secrets.choice(_REFERENCE_ALPHABET) for _ in range(12))
        reference = f"INT-{today}-{suffix}"
        if not Payment.objects.filter(reference=reference).exists():
            return reference
    # Colisión improbable: se amplía el sufijo con token_urlsafe.
    return f"INT-{today}-{secrets.token_urlsafe(12).upper()}"


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
                csv_safe(payment.reference),
                csv_safe(payment.name),
                csv_safe(payment.email),
                csv_safe(payment.phone),
                csv_safe(payment.service),
                payment.amount,
                payment.get_method_display(),
                payment.get_status_display(),
                payment.ip_address or "",
            ]
        )
    return response


def leads_to_csv(queryset):
    """Exportación CSV de leads (reutilizada en core/admin.py)."""
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
                csv_safe(lead.name),
                csv_safe(lead.company),
                csv_safe(lead.email),
                csv_safe(lead.phone),
                csv_safe(lead.service_of_interest),
                lead.get_status_display(),
                lead.ip_address or "",
            ]
        )
    return response


# ---------------------------------------------------------------- Panel de clientes


class ClientLoginForm(AuthenticationForm):
    """Login de cliente con límite de intentos por IP."""

    def clean(self):
        ip = get_client_ip(self.request)
        if not rate_limit(f"login:{ip}", settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_SECONDS):
            raise ValidationError("Demasiados intentos. Espera unos minutos e inténtalo de nuevo.")
        return super().clean()


class ClientLoginView(LoginView):
    """Acceso de clientes con usuario y contraseña."""

    template_name = "panel_login.html"
    redirect_authenticated_user = True
    authentication_form = ClientLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "config": SiteConfig.get_solo(),
                "title": "Acceso de clientes | INTERNETWORK",
                "meta_description": "Consulta tu servicio y tus mensualidades.",
                "canonical": self.request.build_absolute_uri("/panel/"),
            }
        )
        return context

    def get_success_url(self):
        return reverse("core:client_panel")


@noindex
@login_required(login_url="core:client_panel_login")
def client_panel(request):
    """Panel del cliente: su servicio, sus mensualidades y sus datos."""
    profile = getattr(request.user, "client_profile", None)
    charges = profile.charges.all() if profile else []
    pending = [c for c in charges if c.status != "paid"]
    paid = [c for c in charges if c.status == "paid"]
    next_charge = pending[-1] if pending else None

    return render(
        request,
        "panel.html",
        {
            "config": SiteConfig.get_solo(),
            "profile": profile,
            "charges": charges,
            "pending_count": len(pending),
            "paid_count": len(paid),
            "debt": sum(c.amount for c in pending),
            "next_charge": next_charge,
            "title": "Mi panel | INTERNETWORK",
            "meta_description": "Consulta tu servicio y tus mensualidades.",
            "canonical": request.build_absolute_uri("/panel/"),
        },
    )


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /panel/",
        "Disallow: /admin/",
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
