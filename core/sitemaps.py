"""Sitemap para SEO."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import LegalPage


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        return ["core:home", "core:payments"]

    def location(self, item):
        return reverse(item)


class LegalPageSitemap(Sitemap):
    priority = 0.5
    changefreq = "yearly"

    def items(self):
        return LegalPage.objects.filter(active=True)
