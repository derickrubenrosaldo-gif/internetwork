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
    path("panel/acceso/", views.panel_request_link, name="panel_request_link"),
    path("panel/acceso/<str:token>/", views.panel_verify, name="panel_verify"),
    path("panel/salir/", views.panel_logout, name="panel_logout"),
]
