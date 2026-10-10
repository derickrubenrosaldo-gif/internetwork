"""Pruebas: carga de página, creación de Lead, validación, honeypot y rate limit."""

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Differentiator, Lead, Service, SiteConfig, StoryStep


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
