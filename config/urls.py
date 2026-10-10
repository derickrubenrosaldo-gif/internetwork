"""URLs del proyecto INTERNETWORK."""

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.urls import include, path

from core.sitemaps import StaticViewSitemap
from core.views import robots_txt

sitemaps = {"static": StaticViewSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
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
