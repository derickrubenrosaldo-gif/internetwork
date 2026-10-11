"""Pruebas: páginas, pagos, panel de clientes, seguridad, seed y exportaciones."""

import hashlib
import hmac
from datetime import date
from decimal import Decimal
from io import StringIO
from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    ClientProfile,
    Differentiator,
    Lead,
    LegalPage,
    MonthlyCharge,
    Payment,
    Plan,
    Service,
    SiteConfig,
    StoryStep,
)
from .views import leads_to_csv, payments_to_csv


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.config = SiteConfig.get_solo()
        cls.service = Service.objects.create(
            title="Internet dedicado",
            description="Conectividad de alto rendimiento.",
            active=True,
        )
        StoryStep.objects.create(
            label="01 · Internet dedicado",
            title="Una conexión",
            title_highlight="tuya.",
            description="Enlaces estables y de alto rendimiento.",
        )
        Differentiator.objects.create(icon="◉", title="A tu medida", text="Propuestas adaptadas.")

    def setUp(self):
        cache.clear()


class HomePageTests(BaseTestCase):
    def test_home_loads_with_content(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "INTERNETWORK")
        self.assertContains(response, "Internet dedicado")
        self.assertContains(response, "Una conexión")

    def test_home_context_data(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.context["config"], self.config)
        self.assertIn(self.service, response.context["services"])
        self.assertIn("form", response.context)

    def test_seo_tags_present(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, "application/ld+json")
        self.assertContains(response, "LocalBusiness")
        self.assertContains(response, 'rel="canonical"')

    def test_robots_and_sitemap(self):
        self.assertEqual(self.client.get(reverse("robots")).status_code, 200)
        self.assertEqual(self.client.get(reverse("sitemap")).status_code, 200)

    def test_404_page_renders_with_design(self):
        response = self.client.get("/esta-pagina-no-existe/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "no está conectada", status_code=404)


class PlansSectionTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        SiteConfig.objects.update(
            dedicated_features=[
                {"title": "Ancho de banda garantizado", "text": "Velocidad simétrica."}
            ]
        )
        Service.objects.filter(title="Internet dedicado").update(url="#dedicado")
        cls.plan = Plan.objects.create(
            name="Esencial",
            speed="100 Mbps",
            price="$299",
            price_amount=Decimal("299.00"),
            period="/mes",
            tagline="Para tu casa.",
            features=["WiFi incluido", "Instalación gratis"],
        )

    def test_plans_in_context(self):
        response = self.client.get(reverse("core:home"))
        self.assertIn(self.plan, response.context["plans"])

    def test_plans_section_renders(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Internet residencial")
        self.assertContains(response, "Esencial")
        self.assertContains(response, "100 Mbps")
        self.assertContains(response, "$299")
        self.assertContains(response, "WiFi incluido")

    def test_inactive_plan_is_not_shown(self):
        Plan.objects.create(name="Oculto", speed="50 Mbps", active=False)
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, "Oculto")

    def test_popular_plan_shows_badge(self):
        Plan.objects.create(
            name="Familiar",
            speed="300 Mbps",
            price="499",
            price_amount=Decimal("499.00"),
            is_popular=True,
        )
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Más popular")

    def test_dedicated_section_renders(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'id="dedicado"')
        self.assertContains(response, "Ancho de banda exclusivo")
        self.assertContains(response, "Sin compartir.")
        self.assertContains(response, "Ancho de banda garantizado")

    def test_dedicated_service_card_links_to_section(self):
        response = self.client.get(reverse("core:home"))
        self.assertIn("#dedicado", response.content.decode())


class LegalPagesTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.legal = LegalPage.objects.create(
            title="Aviso de privacidad",
            slug="aviso-de-privacidad",
            content="Respeta tu privacidad.\nTus datos están seguros.",
            order=0,
        )

    def test_legal_page_renders(self):
        response = self.client.get(self.legal.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aviso de privacidad")
        self.assertContains(response, "Respeta tu privacidad.")
        self.assertContains(response, "Última actualización")

    def test_legal_page_has_seo_tags(self):
        response = self.client.get(self.legal.get_absolute_url())
        self.assertContains(response, "Aviso de privacidad | INTERNETWORK")
        self.assertContains(response, 'rel="canonical"')

    def test_unknown_slug_returns_404(self):
        response = self.client.get(reverse("core:legal_page", kwargs={"slug": "no-existe"}))
        self.assertEqual(response.status_code, 404)

    def test_inactive_legal_page_returns_404(self):
        LegalPage.objects.create(title="Oculta", slug="oculta", active=False)
        response = self.client.get(reverse("core:legal_page", kwargs={"slug": "oculta"}))
        self.assertEqual(response.status_code, 404)

    def test_footer_shows_legal_links(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "aviso-de-privacidad")
        self.assertContains(response, "Aviso de privacidad")

    def test_sitemap_includes_legal_pages(self):
        response = self.client.get(reverse("sitemap"))
        self.assertContains(response, "/legal/aviso-de-privacidad/")


class PaymentsTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        SiteConfig.objects.update(payment_instructions="")

    valid_payload = {
        "name": "Ana López",
        "email": "ana@acme.com",
        "phone": "555-0100",
        "service": "Internet dedicado",
        "amount": "499.00",
        "method": "transfer",
        "privacy": "on",
        "honeypot": "",
    }

    def test_payments_page_renders(self):
        response = self.client.get(reverse("core:payments"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Genera tu")
        self.assertContains(response, "Transferencia")
        self.assertContains(response, "Generar mi referencia de pago")

    def test_payments_page_shows_coming_soon_without_instructions(self):
        response = self.client.get(reverse("core:payments"))
        self.assertContains(response, "Próximamente")

    def test_payments_page_hides_card_and_cash_without_gateway(self):
        response = self.client.get(reverse("core:payments"))
        self.assertNotContains(response, "checkout seguro de Mercado Pago")
        self.assertNotContains(response, "tiendas de conveniencia")

    def test_payments_page_has_seo_tags(self):
        response = self.client.get(reverse("core:payments"))
        self.assertContains(response, "Pagos | INTERNETWORK")
        self.assertContains(response, 'rel="canonical"')

    def test_valid_payment_is_created(self):
        response = self.client.post(reverse("core:submit_payment"), self.valid_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertTrue(payment.reference.startswith("INT-"))
        self.assertGreaterEqual(len(payment.reference), 20)
        self.assertEqual(payment.status, "pending")
        self.assertIsNone(payment.paid_at)
        self.assertEqual(payment.amount, Decimal("499.00"))
        self.assertEqual(payment.ip_address, "127.0.0.1")
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("reference", data)
        self.assertIn("instructions", data)

    def test_privacy_acceptance_is_required(self):
        payload = dict(self.valid_payload)
        payload.pop("privacy")
        response = self.client.post(reverse("core:submit_payment"), payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)
        self.assertIn("privacy", response.json()["errors"])

    def test_negative_amount_is_rejected(self):
        payload = dict(self.valid_payload, amount="-10")
        response = self.client.post(reverse("core:submit_payment"), payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)
        self.assertIn("amount", response.json()["errors"])

    def test_amount_above_cap_is_rejected(self):
        payload = dict(self.valid_payload, amount="99999999")
        response = self.client.post(reverse("core:submit_payment"), payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)
        self.assertIn("amount", response.json()["errors"])

    def test_service_must_be_real(self):
        payload = dict(self.valid_payload, service="<script>alert(1)</script>")
        response = self.client.post(reverse("core:submit_payment"), payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)

    def test_plan_amount_comes_from_the_plan(self):
        Plan.objects.create(
            name="Plan real",
            speed="300 Mbps",
            price="$500",
            price_amount=Decimal("500.00"),
            active=True,
        )
        payload = dict(self.valid_payload, service="Plan real", amount="1.00")
        response = self.client.post(reverse("core:submit_payment"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.first().amount, Decimal("500.00"))

    def test_plan_without_price_is_not_offered(self):
        Plan.objects.create(name="Sin precio", active=True)
        response = self.client.get(reverse("core:payments"))
        self.assertNotContains(response, "Sin precio")

    def test_invalid_payment_returns_errors(self):
        response = self.client.post(
            reverse("core:submit_payment"),
            {"name": "", "email": "no-correo", "privacy": "on", "honeypot": ""},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("errors", data)

    def test_honeypot_blocks_bots_silently(self):
        payload = dict(self.valid_payload, honeypot="relleno")
        response = self.client.post(reverse("core:submit_payment"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 0)

    def test_rate_limit_by_ip(self):
        url = reverse("core:submit_payment")
        with override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_SECONDS=60):
            self.client.post(url, self.valid_payload)
            self.client.post(url, self.valid_payload)
            response = self.client.post(url, self.valid_payload)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(Payment.objects.count(), 2)
        self.assertIn("Demasiados intentos", response.json()["message"])

    def test_get_not_allowed(self):
        response = self.client.get(reverse("core:submit_payment"))
        self.assertEqual(response.status_code, 405)

    def test_sitemap_includes_payments(self):
        response = self.client.get(reverse("sitemap"))
        self.assertContains(response, "/pagos/")


class LeadSubmissionTests(BaseTestCase):
    valid_payload = {
        "name": "Ana López",
        "company": "Acme",
        "email": "ana@acme.com",
        "phone": "555-0100",
        "service_of_interest": "Internet dedicado",
        "message": "Necesito internet para mi oficina.",
        "privacy": "on",
        "honeypot": "",
    }

    def test_valid_lead_is_created(self):
        response = self.client.post(reverse("core:submit_lead"), self.valid_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 1)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        lead = Lead.objects.first()
        self.assertEqual(lead.name, "Ana López")
        self.assertEqual(lead.ip_address, "127.0.0.1")

    def test_privacy_acceptance_is_required(self):
        payload = dict(self.valid_payload)
        payload.pop("privacy")
        response = self.client.post(reverse("core:submit_lead"), payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Lead.objects.count(), 0)

    def test_invalid_lead_returns_field_errors(self):
        response = self.client.post(
            reverse("core:submit_lead"),
            {
                "name": "",
                "email": "no-correo",
                "service_of_interest": "",
                "privacy": "on",
                "honeypot": "",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Lead.objects.count(), 0)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("errors", data)
        self.assertIn("name", data["errors"])

    def test_honeypot_blocks_bots_silently(self):
        payload = dict(self.valid_payload, honeypot="relleno")
        response = self.client.post(reverse("core:submit_lead"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)
        self.assertEqual(response.json()["status"], "ok")

    def test_rate_limit_by_ip(self):
        url = reverse("core:submit_lead")
        with override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_SECONDS=60):
            self.client.post(url, self.valid_payload)
            self.client.post(url, self.valid_payload)
            response = self.client.post(url, self.valid_payload)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(Lead.objects.count(), 2)
        self.assertIn("Demasiadas solicitudes", response.json()["message"])

    def test_whatsapp_url_uses_percent_0a_separator(self):
        with override_settings(WHATSAPP_NUMBER="5219511234567"):
            response = self.client.post(reverse("core:submit_lead"), self.valid_payload)
        url = response.json()["whatsapp_url"]
        self.assertIn("https://wa.me/5219511234567", url)
        self.assertIn("Ana%20L%C3%B3pez", url)
        self.assertIn("%0A", url)
        self.assertNotIn("%n", url)

    def test_no_whatsapp_url_when_not_configured(self):
        response = self.client.post(reverse("core:submit_lead"), self.valid_payload)
        self.assertIsNone(response.json()["whatsapp_url"])

    def test_get_not_allowed(self):
        response = self.client.get(reverse("core:submit_lead"))
        self.assertEqual(response.status_code, 405)


class ClientPanelTests(BaseTestCase):
    """Panel del cliente: login con usuario y contraseña y dashboard propio."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user("ana", "ana@acme.com", "ClaveSegura123")
        cls.profile = ClientProfile.objects.create(
            user=cls.user,
            full_name="Ana López",
            phone="555-0100",
            address="Calle Managua 4",
            customer_code="C-001",
            monthly_amount=Decimal("480.00"),
            billing_day=5,
        )
        cls.charge = MonthlyCharge.objects.create(
            client=cls.profile,
            period="2026-10",
            amount=Decimal("480.00"),
            due_date=date(2026, 10, 5),
        )
        cls.other = User.objects.create_user("beto", "beto@otro.com", "OtraClave123")
        cls.other_profile = ClientProfile.objects.create(user=cls.other, full_name="Beto Ruiz")
        MonthlyCharge.objects.create(
            client=cls.other_profile,
            period="2026-10",
            amount=Decimal("9999.00"),
            due_date=date(2026, 10, 9),
            reference="OTRO-CLIENTE",
        )

    def test_login_page_renders_with_user_and_password(self):
        response = self.client.get(reverse("core:client_panel"))
        self.assertEqual(response.status_code, 302)  # redirige al acceso
        page = self.client.get(reverse("core:client_panel_login"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'name="username"')
        self.assertContains(page, 'name="password"')
        self.assertNotContains(page, 'name="reference"')

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("core:client_panel_login"),
            {"username": "ana", "password": "ClaveSegura123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("core:client_panel"))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            reverse("core:client_panel_login"), {"username": "ana", "password": "mala"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("core:client_panel"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("core:client_panel_login"), response.url)

    def test_dashboard_shows_own_service_and_charges(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:client_panel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana López")
        self.assertContains(response, "2026-10")
        self.assertContains(response, "480,00")

    def test_dashboard_does_not_leak_other_clients(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:client_panel"))
        self.assertNotContains(response, "OTRO-CLIENTE")
        self.assertNotContains(response, "9999.00")
        self.assertNotContains(response, "Beto Ruiz")

    def test_debt_counts_only_pending(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:client_panel"))
        self.assertEqual(response.context["debt"], Decimal("480.00"))
        self.assertEqual(response.context["pending_count"], 1)

    def test_panel_sets_noindex_header(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:client_panel"))
        self.assertIn("noindex", response["X-Robots-Tag"])

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("core:client_panel_logout")).status_code, 405)

    def test_logout_clears_session(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("core:client_panel_logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_is_rate_limited(self):
        url = reverse("core:client_panel_login")
        with override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_SECONDS=60):
            self.client.post(url, {"username": "ana", "password": "mala"})
            self.client.post(url, {"username": "ana", "password": "mala"})
            response = self.client.post(url, {"username": "ana", "password": "mala"})
        self.assertContains(response, "Demasiados intentos")


class MercadoPagoWebhookTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.payment = Payment.objects.create(
            name="Ana López",
            email="ana@acme.com",
            service="Internet dedicado",
            amount=Decimal("499.00"),
            method="card",
            reference="INT-20261010-AB12CD34EF56",
        )

    def _headers(self, data_id="123", ts="1700000000", request_id="req-1"):
        manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
        signature = hmac.new(b"s3cr3t", manifest.encode(), hashlib.sha256).hexdigest()
        return {
            "HTTP_X_SIGNATURE": f"ts={ts},v1={signature}",
            "HTTP_X_REQUEST_ID": request_id,
        }

    @override_settings(MP_WEBHOOK_SECRET="s3cr3t", MP_ACCESS_TOKEN="tok")
    def test_invalid_signature_is_rejected(self):
        response = self.client.post(
            reverse("core:payment_webhook") + "?data.id=123",
            HTTP_X_SIGNATURE="ts=1,v1=malo",
        )
        self.assertEqual(response.status_code, 401)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "pending")

    @override_settings(MP_WEBHOOK_SECRET="", MP_ACCESS_TOKEN="tok")
    def test_webhook_rejected_without_secret(self):
        response = self.client.post(
            reverse("core:payment_webhook") + "?data.id=123", **self._headers()
        )
        self.assertEqual(response.status_code, 401)

    @override_settings(MP_WEBHOOK_SECRET="s3cr3t", MP_ACCESS_TOKEN="tok")
    def test_approved_payment_marks_paid(self):
        remote = {
            "id": 123,
            "status": "approved",
            "external_reference": self.payment.reference,
        }
        with mock.patch("core.views.mp.fetch_payment", return_value=remote):
            response = self.client.post(
                reverse("core:payment_webhook") + "?data.id=123", **self._headers()
            )
        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "paid")
        self.assertIsNotNone(self.payment.paid_at)
        self.assertEqual(self.payment.provider, "mercadopago")

    @override_settings(MP_WEBHOOK_SECRET="s3cr3t", MP_ACCESS_TOKEN="tok")
    def test_webhook_is_idempotent(self):
        remote = {
            "id": 123,
            "status": "approved",
            "external_reference": self.payment.reference,
        }
        with mock.patch("core.views.mp.fetch_payment", return_value=remote):
            self.client.post(reverse("core:payment_webhook") + "?data.id=123", **self._headers())
        self.payment.refresh_from_db()
        first_paid_at = self.payment.paid_at
        with mock.patch("core.views.mp.fetch_payment", return_value=remote):
            self.client.post(reverse("core:payment_webhook") + "?data.id=123", **self._headers())
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.paid_at, first_paid_at)


class CsvExportTests(BaseTestCase):
    def test_formula_injection_is_neutralized(self):
        Lead.objects.create(
            name="=1+1",
            email="ana@acme.com",
            service_of_interest="@SUM(A1)",
        )
        response = leads_to_csv(Lead.objects.all())
        body = response.content.decode()
        # El valor peligroso queda como texto, no como fórmula.
        self.assertIn("'=1+1", body)
        self.assertIn("'@SUM(A1)", body)

    def test_payment_csv_neutralizes_formula(self):
        Payment.objects.create(
            name="-2+3",
            email="ana@acme.com",
            service="+Internet",
            amount=Decimal("10.00"),
            method="transfer",
            reference="INT-20261010-AB12CD34EF56",
        )
        response = payments_to_csv(Payment.objects.all())
        body = response.content.decode()
        self.assertIn("'-2+3", body)
        self.assertIn("'+Internet", body)


class SeedTests(BaseTestCase):
    """El seed nunca debe pisar lo editado en el admin."""

    def test_default_seed_does_not_overwrite(self):
        self.service.title = "Editado a mano"
        self.service.save()
        call_command("seed_site", stdout=StringIO())
        self.service.refresh_from_db()
        self.assertEqual(self.service.title, "Editado a mano")

    def test_force_seed_overwrites(self):
        self.service.title = "Editado a mano"
        self.service.save()
        call_command("seed_site", "--reset", "--force", stdout=StringIO())
        titles = list(Service.objects.values_list("title", flat=True))
        self.assertIn("Internet dedicado", titles)

    def test_default_seed_loads_real_data_without_inventing(self):
        call_command("seed_site", "--force", stdout=StringIO())
        config = SiteConfig.get_solo()
        # Datos reales del negocio.
        self.assertEqual(config.whatsapp, "9211200027")
        self.assertIn("Minatitlán", config.address)
        self.assertEqual(Plan.objects.count(), 3)
        prices = sorted(str(p.price_amount) for p in Plan.objects.all())
        self.assertEqual(prices, ["380.00", "480.00", "600.00"])
        # Nada inventado: sin cifras, sin "Más popular" ni características.
        self.assertEqual(config.stats, [])
        self.assertFalse(Plan.objects.filter(is_popular=True).exists())
        self.assertFalse(any(p.features for p in Plan.objects.all()))

    def test_demo_seed_marks_examples(self):
        call_command("seed_site", "--force", "--demo", stdout=StringIO())
        config = SiteConfig.get_solo()
        self.assertTrue(config.stats)  # cifras de ejemplo, solo con --demo


class CoverageTests(BaseTestCase):
    def test_coverage_is_parsed_and_grouped(self):
        SiteConfig.objects.update(
            coverage_zones=(
                "Allende — Coatzacoalcos\nMapachapa — Minatitlán\nNanchital — Nanchital"
            )
        )
        config = SiteConfig.get_solo()
        self.assertEqual(config.coverage_count, 3)
        self.assertEqual(config.zones_list, ["Allende", "Mapachapa", "Nanchital"])
        self.assertEqual(
            config.coverage_municipalities, ["Coatzacoalcos", "Minatitlán", "Nanchital"]
        )
        grouped = config.coverage_grouped
        self.assertEqual(grouped[0]["municipality"], "Coatzacoalcos")
        self.assertEqual(grouped[0]["localities"], ["Allende"])

    def test_coverage_section_renders_with_real_localities(self):
        SiteConfig.objects.update(coverage_zones="Mapachapa — Minatitlán")
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'id="cobertura"')
        self.assertContains(response, "Mapachapa")
        self.assertContains(response, "Minatitlán")
        self.assertContains(response, "¿Llegan a mi zona?")
