"""Formulario de contacto con validación en servidor y honeypot anti-spam."""

from django import forms

from .models import Lead, Service


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
