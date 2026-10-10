"""Administración del sitio INTERNETWORK."""

from django.contrib import admin

from .models import Differentiator, Lead, Service, SiteConfig, StoryStep
from .views import leads_to_csv


@admin.register(SiteConfig)
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
    )

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "active")
    list_editable = ("order", "active")
    list_filter = ("active",)
    search_fields = ("title",)
    prepopulated_fields = {}


@admin.register(StoryStep)
class StoryStepAdmin(admin.ModelAdmin):
    list_display = ("label", "order")
    list_editable = ("order",)


@admin.register(Differentiator)
class DifferentiatorAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service_of_interest", "status", "created_at")
    list_filter = ("status", "service_of_interest", "created_at")
    search_fields = ("name", "email", "company", "phone", "message")
    date_hierarchy = "created_at"
    list_per_page = 40
    actions = ["export_csv"]

    @admin.action(description="Exportar selección a CSV")
    def export_csv(self, request, queryset):
        return leads_to_csv(queryset)
