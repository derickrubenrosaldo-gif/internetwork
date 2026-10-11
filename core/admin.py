"""Administración del sitio INTERNETWORK.

Panel propio (InternetworkAdminSite): branding, dashboard de resumen
en el índice y acciones masivas para solicitudes y pagos.
"""

from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone

from .models import (
    Differentiator,
    Lead,
    LegalPage,
    Payment,
    Plan,
    Service,
    SiteConfig,
    StoryStep,
    UsedLoginToken,
)
from .views import leads_to_csv, payments_to_csv


class InternetworkAdminSite(admin.AdminSite):
    """Panel de INTERNETWORK: branding + dashboard en el índice."""

    site_header = "INTERNETWORK"
    site_title = "INTERNETWORK · Panel"
    index_title = "Panel de control"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        pending = Payment.objects.filter(status="pending")
        extra_context["dashboard"] = {
            "leads": Lead.objects.count(),
            "new_leads": Lead.objects.filter(status="new").count(),
            "payments_pending": pending.count(),
            "payments_paid": Payment.objects.filter(status="paid").count(),
            "pending_amount": pending.aggregate(total=Sum("amount"))["total"] or 0,
            "services": Service.objects.count(),
            "plans": Plan.objects.count(),
            "legal_pages": LegalPage.objects.count(),
        }
        extra_context["recent_leads"] = Lead.objects.order_by("-created_at")[:5]
        extra_context["recent_payments"] = Payment.objects.order_by("-created_at")[:5]
        return super().index(request, extra_context)


admin_site = InternetworkAdminSite(name="admin")


@admin.register(SiteConfig, site=admin_site)
class SiteConfigAdmin(admin.ModelAdmin):
    """Singleton: solo puede existir un registro."""

    fieldsets = (
        ("Contacto", {"fields": ("email", "phone", "whatsapp", "address", "coverage_zones")}),
        (
            "Hero",
            {"fields": ("hero_eyebrow", "hero_title", "hero_title_highlight", "hero_subtitle")},
        ),
        ("Manifiesto", {"fields": ("statement_text",)}),
        (
            "Zonas rurales",
            {"fields": ("rural_title", "rural_title_highlight", "rural_description")},
        ),
        ("Resultados", {"fields": ("stats",)}),
        ("Redes sociales", {"fields": ("socials",)}),
        (
            "Internet dedicado",
            {
                "fields": (
                    "dedicated_title",
                    "dedicated_title_highlight",
                    "dedicated_description",
                    "dedicated_features",
                )
            },
        ),
        ("Pagos", {"fields": ("payment_instructions",)}),
    )

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Service, site=admin_site)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "active")
    list_editable = ("order", "active")
    list_filter = ("active",)
    search_fields = ("title",)


@admin.register(Plan, site=admin_site)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "speed", "price", "is_popular", "order", "active")
    list_editable = ("is_popular", "order", "active")
    list_filter = ("is_popular", "active")
    search_fields = ("name", "speed")


@admin.register(StoryStep, site=admin_site)
class StoryStepAdmin(admin.ModelAdmin):
    list_display = ("label", "title", "order")
    list_editable = ("order",)
    search_fields = ("label", "title")


@admin.register(Differentiator, site=admin_site)
class DifferentiatorAdmin(admin.ModelAdmin):
    list_display = ("icon", "title", "order")
    list_editable = ("order",)
    search_fields = ("title",)


@admin.register(LegalPage, site=admin_site)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "updated_at", "order", "active")
    list_editable = ("order", "active")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)


@admin.register(Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "name",
        "service",
        "amount",
        "method",
        "status",
        "paid_at",
        "created_at",
    )
    list_filter = ("status", "method", "provider")
    search_fields = ("reference", "name", "email", "service", "provider_ref")
    date_hierarchy = "created_at"
    list_per_page = 40
    readonly_fields = ("provider", "provider_ref", "paid_at", "confirmed_by")
    actions = ["export_csv", "mark_paid"]

    @admin.action(description="Exportar selección a CSV")
    def export_csv(self, request, queryset):
        return payments_to_csv(queryset)

    @admin.action(description="Marcar como pagado")
    def mark_paid(self, request, queryset):
        updated = queryset.update(status="paid", paid_at=timezone.now(), confirmed_by=request.user)
        self.message_user(request, f"{updated} pago(s) marcados como pagados.")


@admin.register(UsedLoginToken, site=admin_site)
class UsedLoginTokenAdmin(admin.ModelAdmin):
    list_display = ("nonce", "email", "created_at")
    search_fields = ("nonce", "email")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False


@admin.register(Lead, site=admin_site)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service_of_interest", "status", "created_at")
    list_filter = ("status", "service_of_interest", "created_at")
    search_fields = ("name", "email", "company", "phone", "message")
    date_hierarchy = "created_at"
    list_per_page = 40
    actions = ["export_csv", "mark_contacted"]

    @admin.action(description="Exportar selección a CSV")
    def export_csv(self, request, queryset):
        return leads_to_csv(queryset)

    @admin.action(description="Marcar como contactado")
    def mark_contacted(self, request, queryset):
        updated = queryset.update(status="contacted")
        self.message_user(request, f"{updated} solicitud(es) marcadas como contactadas.")
