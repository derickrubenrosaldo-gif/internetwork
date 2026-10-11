"""Formularios con validación en servidor y honeypot anti-spam."""

from django import forms

from .models import Lead, Payment, Plan, Service


class LeadForm(forms.ModelForm):
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
        help_texts = {
            "name": "",
            "email": "",
        }

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

    def clean_honeypot(self):
        # Si el campo oculto tiene contenido, es un bot: el vista lo ignora.
        return self.cleaned_data.get("honeypot", "")


class PaymentForm(forms.ModelForm):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["email"].required = True
        self.fields["service"].required = True
        self.fields["amount"].required = True
        self.fields["method"].required = True
        choices = [("", "Selecciona qué pagas")]
        choices += [
            (s.title, f"Servicio: {s.title}")
            for s in Service.objects.filter(active=True).order_by("order")
        ]
        choices += [
            (p.name, f"Plan {p.name} ({p.speed})")
            for p in Plan.objects.filter(active=True).order_by("order")
        ]
        choices.append(("Otro servicio", "Otro servicio"))
        self.fields["service"].widget = forms.Select(choices=choices)
        self.fields["method"].choices = [
            ("", "Selecciona un método"),
            *Payment.METHOD_CHOICES,
        ]
