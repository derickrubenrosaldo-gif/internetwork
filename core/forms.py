"""Formularios de contacto y de pagos."""

from django import forms
from django.conf import settings

from .models import Lead, Payment, Plan, Service


class PrivacyMixin(forms.Form):
    """Casilla obligatoria de aceptación del aviso de privacidad."""

    privacy = forms.BooleanField(
        required=True,
        label="He leído y acepto el aviso de privacidad",
        error_messages={"required": "Debes aceptar el aviso de privacidad para continuar."},
        widget=forms.CheckboxInput(attrs={"class": "privacy-check"}),
    )


class LeadForm(PrivacyMixin, forms.ModelForm):
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
        label="",
    )

    class Meta:
        model = Lead
        fields = ["name", "company", "email", "phone", "service_of_interest", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Tu nombre"}),
            "company": forms.TextInput(attrs={"placeholder": "Opcional"}),
            "email": forms.EmailInput(attrs={"placeholder": "tu@correo.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "Tu número"}),
            "message": forms.Textarea(
                attrs={"placeholder": "Ubicación, necesidades, alcance aproximado..."}
            ),
        }
        labels = {
            "name": "Nombre",
            "company": "Empresa",
            "email": "Correo",
            "phone": "Teléfono",
            "service_of_interest": "Servicio de interés",
            "message": "Cuéntanos tu proyecto",
        }
        help_texts = {"name": "", "email": ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["email"].required = True
        choices = [("", "Selecciona un servicio")]
        choices += [
            (s.title, s.title) for s in Service.objects.filter(active=True).order_by("order")
        ]
        choices.append(("Otro proyecto", "Otro proyecto"))
        self.fields["service_of_interest"].widget = forms.Select(choices=choices)
        self.fields["service_of_interest"].required = True
        self.allowed_services = {value for value, _ in choices if value}

    def clean_service_of_interest(self):
        value = self.cleaned_data.get("service_of_interest", "")
        if value and value not in self.allowed_services:
            raise forms.ValidationError("Selecciona un servicio de la lista.")
        return value


class PaymentForm(PrivacyMixin, forms.ModelForm):
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
        label="",
    )

    class Meta:
        model = Payment
        fields = ["name", "email", "phone", "service", "amount", "method"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Tu nombre"}),
            "email": forms.EmailInput(attrs={"placeholder": "tu@correo.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "Tu número"}),
            "service": forms.Select(),
            "amount": forms.NumberInput(
                attrs={"placeholder": "Monto a pagar", "min": "1", "step": "0.01"}
            ),
            "method": forms.Select(),
        }
        labels = {
            "name": "Nombre",
            "email": "Correo",
            "phone": "Teléfono",
            "service": "Servicio o plan",
            "amount": "Monto",
            "method": "Método de pago",
        }
        help_texts = {"name": "", "email": ""}

    def __init__(self, *args, methods=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_amount = settings.PAYMENT_MAX_AMOUNT
        for name in ("name", "email", "service", "amount", "method"):
            self.fields[name].required = True

        # Solo se ofrecen servicios reales y planes con precio real.
        self._plans = {
            p.name: p for p in Plan.objects.filter(active=True, price_amount__isnull=False)
        }
        choices = [("", "Selecciona qué pagas")]
        choices += [
            (s.title, f"Servicio: {s.title}")
            for s in Service.objects.filter(active=True).order_by("order")
        ]
        choices += [(p.name, f"Plan {p.name} ({p.speed})") for p in self._plans.values()]
        choices.append(("Otro servicio", "Otro servicio"))
        self.fields["service"].widget = forms.Select(choices=choices)
        self.allowed_services = {value for value, _ in choices if value}

        self.fields["method"].choices = [
            ("", "Selecciona un método"),
            *(methods if methods is not None else [(m[0], m[1]) for m in Payment.METHOD_CHOICES]),
        ]

    def clean(self):
        cleaned = super().clean()
        service = cleaned.get("service")
        if service and service not in self.allowed_services:
            self.add_error("service", "Selecciona un servicio de la lista.")

        amount = cleaned.get("amount")
        plan = self._plans.get(service)

        # Si el pago es de un plan con precio real, el monto sale del plan.
        if plan is not None and plan.price_amount is not None:
            amount = plan.price_amount
            cleaned["amount"] = amount
            self.instance.amount = amount

        if amount is not None:
            if amount <= 0:
                self.add_error("amount", "El monto debe ser mayor que cero.")
            elif amount > self.max_amount:
                self.add_error(
                    "amount",
                    f"El monto no puede superar {self.max_amount:.0f}. "
                    "Si tu pago es mayor, contáctanos.",
                )
        return cleaned
