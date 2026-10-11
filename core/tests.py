"""Pruebas: carga de página, pagos, creación de Lead, validación, honeypot y rate limit."""

from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    Differentiator,
    Lead,
    LegalPage,
    Payment,
    Plan,
    Service,
    SiteConfig,
    StoryStep,
)


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
        Plan.objects.create(name="Familiar", speed="300 Mbps", is_popular=True)
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
        self.assertIn('#dedicado', response.content.decode())


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
        SiteConfig.objects.update(
            payment_instructions="Banco Ejemplo, Cuenta: 0123456789."
        )
    valid_payload = {
        "name": "Ana López",
        "email": "ana@acme.com",
        "phone": "555-0100",
        "service": "Internet dedicado",
        "amount": "499.00",
        "method": "transfer",
        "honeypot": "",
    }

    def test_payments_page_renders(self):
        response = self.client.get(reverse("core:payments"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Realiza tu")
        self.assertContains(response, "Transferencia")
        self.assertContains(response, "Datos para transferir")

    def test_payments_page_has_seo_tags(self):
        response = self.client.get(reverse("core:payments"))
        self.assertContains(response, "Pagos | INTERNETWORK")
        self.assertContains(response, 'rel="canonical"')

    def test_valid_payment_is_created(self):
        response = self.client.post(
            reverse("core:submit_payment"), self.valid_payload
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertTrue(payment.reference.startswith("INT-"))
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.amount, Decimal("499.00"))
        self.assertEqual(payment.ip_address, "127.0.0.1")
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("reference", data)
        self.assertIn("instructions", data)

    def test_invalid_payment_returns_errors(self):
        response = self.client.post(
            reverse("core:submit_payment"),
            {"name": "", "email": "no-correo", "honeypot": ""},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("errors", data)

    def test_honeypot_blocks_bots_silently(self):
        payload = dict(self.valid_payload, honeypot="relleno")
        response = self.client.post(
            reverse("core:submit_payment"), payload
        )
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

    def test_invalid_lead_returns_field_errors(self):
        response = self.client.post(
            reverse("core:submit_lead"),
            {"name": "", "email": "no-correo", "service_of_interest": "", "honeypot": ""},
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

    def test_whatsapp_url_when_configured(self):
        with override_settings(WHATSAPP_NUMBER="5219511234567"):
            response = self.client.post(reverse("core:submit_lead"), self.valid_payload)
        data = response.json()
        self.assertIn("https://wa.me/5219511234567", data["whatsapp_url"])
        self.assertIn("Ana%20L%C3%B3pez", data["whatsapp_url"])

    def test_no_whatsapp_url_when_not_configured(self):
        response = self.client.post(reverse("core:submit_lead"), self.valid_payload)
        self.assertIsNone(response.json()["whatsapp_url"])

    def test_get_not_allowed(self):
        response = self.client.get(reverse("core:submit_lead"))
        self.assertEqual(response.status_code, 405)


class ClientPanelTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.payment = Payment.objects.create(
            name="Ana López",
            email="ana@acme.com",
            service="Familiar",
            amount=Decimal("499.00"),
            method="transfer",
            reference="INT-20261010-AB12",
        )

    def test_panel_login_page_renders(self):
        response = self.client.get(reverse("core:client_panel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Panel de clientes")
        self.assertContains(response, 'id="id_email"')
        self.assertContains(response, 'id="id_reference"')

    def test_login_with_valid_reference(self):
        response = self.client.post(
            reverse("core:client_login"),
            {"email": "ana@acme.com", "reference": "INT-20261010-AB12"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["client_email"], "ana@acme.com")

    def test_login_is_case_insensitive(self):
        response = self.client.post(
            reverse("core:client_login"),
            {"email": "ANA@ACME.COM", "reference": "int-20261010-ab12"},
        )
        self.assertEqual(response.status_code, 302)

    def test_login_with_invalid_reference(self):
        response = self.client.post(
            reverse("core:client_login"),
            {"email": "ana@acme.com", "reference": "NOPE"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No encontramos ese pago")
        self.assertNotIn("client_email", self.client.session)

    def test_panel_lists_payments_when_logged_in(self):
        self.client.post(
            reverse("core:client_login"),
            {"email": "ana@acme.com", "reference": "INT-20261010-AB12"},
        )
        response = self.client.get(reverse("core:client_panel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "INT-20261010-AB12")
        self.assertContains(response, "Familiar")
        self.assertContains(response, "ana@acme.com")

    def test_panel_shows_totals(self):
        self.client.post(
            reverse("core:client_login"),
            {"email": "ana@acme.com", "reference": "INT-20261010-AB12"},
        )
        response = self.client.get(reverse("core:client_panel"))
        self.assertEqual(response.context["total_pending"], Decimal("499.00"))
        self.assertEqual(response.context["total_paid"], Decimal("0.00"))

    def test_panel_denies_direct_access_without_login(self):
        response = self.client.get(reverse("core:client_panel"))
        self.assertContains(response, "Panel de clientes")
        self.assertNotContains(response, "Mi cuenta")

    def test_logout_clears_session(self):
        self.client.post(
            reverse("core:client_login"),
            {"email": "ana@acme.com", "reference": "INT-20261010-AB12"},
        )
        response = self.client.get(reverse("core:client_logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("client_email", self.client.session)
