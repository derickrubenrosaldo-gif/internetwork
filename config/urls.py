"""URLs del proyecto INTERNETWORK."""

from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.urls import include, path

from core.admin import admin_site
from core.sitemaps import LegalPageSitemap, StaticViewSitemap
from core.views import robots_txt

sitemaps = {"static": StaticViewSitemap, "legal": LegalPageSitemap}

urlpatterns = [
    path("admin/", admin_site.urls),
    path("", include("core.urls")),
    path("robots.txt", robots_txt, name="robots"),
    path(
        "sitemap.xml",
        sitemap_view,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),
]

handler404 = "core.views.page_not_found"
handler500 = "core.views.server_error"
