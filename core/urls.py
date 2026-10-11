from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("contacto/enviar/", views.submit_lead, name="submit_lead"),
    path("legal/<slug:slug>/", views.legal_page, name="legal_page"),
    path("pagos/", views.payments_page, name="payments"),
    path("pagos/enviar/", views.submit_payment, name="submit_payment"),
    path("pagos/webhook/mercadopago/", views.payment_webhook, name="payment_webhook"),
    path("panel/", views.client_panel, name="client_panel"),
    path("panel/entrar/", views.ClientLoginView.as_view(), name="client_panel_login"),
    path(
        "panel/salir/",
        LogoutView.as_view(next_page="core:client_panel"),
        name="client_panel_logout",
    ),
]
