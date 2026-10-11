"""Modelos del sitio INTERNETWORK — todo editable desde el admin."""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class SiteConfig(models.Model):
    """Configuración global del sitio (singleton: un solo registro)."""

    email = models.EmailField("Correo de contacto", blank=True, default="")
    phone = models.CharField("Teléfono", max_length=40, blank=True, default="")
    whatsapp = models.CharField(
        "WhatsApp (código de país + número, sin +)",
        max_length=25,
        blank=True,
        default="",
        help_text="Ej: 5219511234567",
    )
    address = models.CharField("Dirección", max_length=255, blank=True, default="")
    coverage_zones = models.TextField(
        "Zonas de cobertura",
        blank=True,
        default="",
        help_text="Separadas por comas. Ej: Ciudad de México, Guadalajara, Monterrey",
    )

    hero_eyebrow = models.CharField(
        "Hero · etiqueta", max_length=120, default="Conectando tu mundo"
    )
    hero_title = models.CharField("Hero · título", max_length=120, default="Internet sin")
    hero_title_highlight = models.CharField(
        "Hero · resaltado en degradado", max_length=120, default="límites."
    )
    hero_subtitle = models.TextField(
        "Hero · subtítulo",
        default="Internet dedicado, soluciones IT, infraestructura y software. Llegamos hasta donde otros no llegan.",
    )
    statement_text = models.TextField(
        "Manifiesto",
        default="Somos INTERNETWORK. Una sola empresa para conectar tu negocio, tu comunidad y tu hogar, con la tecnología que necesitas para crecer.",
    )
    rural_title = models.CharField(
        "Zonas rurales · título", max_length=200, default="La distancia no debería limitar tus"
    )
    rural_title_highlight = models.CharField(
        "Zonas rurales · resaltado", max_length=120, default="oportunidades."
    )
    rural_description = models.TextField(
        "Zonas rurales · descripción",
        default="Acercamos servicios digitales a comunidades rurales, comercios, instituciones y hogares que necesitan estar conectados.",
    )
    stats = models.JSONField(
        "Resultados (banda de cifras)",
        default=list,
        blank=True,
        help_text='Lista de {"value": "+500", "label": "Negocios conectados"}.',
    )
    socials = models.JSONField(
        "Redes sociales",
        default=list,
        blank=True,
        help_text='Lista de {"name": "...", "url": "https://..."}.',
    )
    dedicated_title = models.CharField(
        "Internet dedicado · título",
        max_length=200,
        default="Ancho de banda exclusivo para tu operación.",
    )
    dedicated_title_highlight = models.CharField(
        "Internet dedicado · resaltado", max_length=120, default="Sin compartir."
    )
    dedicated_description = models.TextField(
        "Internet dedicado · descripción",
        default=(
            "El internet dedicado te asigna una conexión privada y simétrica: "
            "toda la capacidad es para tu negocio, con respuesta garantizada "
            "y monitoreo continuo."
        ),
    )
    dedicated_features = models.JSONField(
        "Internet dedicado · características",
        default=list,
        blank=True,
        help_text='Lista de {"title": "...", "text": "..."}.',
    )
    payment_instructions = models.TextField(
        "Pagos · instrucciones bancarias",
        blank=True,
        default="",
        help_text="Datos de cuenta o instrucciones para transferir.",
    )

    class Meta:
        verbose_name = "Configuración del sitio"
        verbose_name_plural = "Configuración del sitio"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("La configuración del sitio no se puede eliminar.")

    @classmethod
    def get_solo(cls):
        return cls.objects.get_or_create(pk=1)[0]

    @property
    def coverage_list(self):
        """Pares (localidad, municipio) del texto de cobertura.

        Acepta una entrada por línea con el formato "Localidad — Municipio"
        (también admite valores separados por comas y sin municipio).
        """
        areas = []
        for raw in self.coverage_zones.replace(",", "\n").splitlines():
            line = raw.strip()
            if not line:
                continue
            if " — " in line:
                locality, municipality = line.split(" — ", 1)
            else:
                locality, municipality = line, ""
            areas.append((locality.strip(), municipality.strip()))
        return areas

    @property
    def zones_list(self):
        """Nombres de localidad cubiertas."""
        return [locality for locality, _ in self.coverage_list]

    @property
    def coverage_municipalities(self):
        """Municipios distintos cubiertos (para SEO y resúmenes)."""
        return sorted({municipality for _, municipality in self.coverage_list if municipality})

    @property
    def coverage_grouped(self):
        """Cobertura agrupada por municipio, en orden alfabético."""
        groups = {}
        for locality, municipality in self.coverage_list:
            groups.setdefault(municipality or "Otras localidades", []).append(locality)
        return [{"municipality": key, "localities": sorted(groups[key])} for key in sorted(groups)]

    @property
    def coverage_count(self):
        """Número de localidades cubiertas."""
        return len(self.coverage_list)

    @property
    def whatsapp_url(self):
        """Enlace de WhatsApp (vacío si no hay número configurado)."""
        if not self.whatsapp:
            return ""
        return f"https://wa.me/{self.whatsapp}"

    def __str__(self):
        return "Configuración del sitio"


class Service(models.Model):
    """Servicio mostrado en la banda horizontal de servicios."""

    title = models.CharField("Título", max_length=120)
    description = models.TextField("Descripción", max_length=400)
    icon = models.CharField(
        "Ícono (carácter)",
        max_length=8,
        default="◈",
        help_text="Carácter mostrado si no hay archivo Lottie. Ej: ⌁ ☁ ♧ ▤",
    )
    lottie_file = models.CharField(
        "Archivo Lottie (opcional)",
        max_length=120,
        blank=True,
        default="",
        help_text="Nombre del archivo en static/lottie/. Ej: signal.json",
    )
    url = models.CharField("Enlace (ancla o URL)", max_length=255, default="#contacto")
    link_text = models.CharField("Texto del enlace", max_length=80, default="Solicitar información")
    order = models.PositiveIntegerField("Orden", default=0)
    active = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.title


class Plan(models.Model):
    """Plan de internet residencial mostrado en la sección 'Planes'."""

    name = models.CharField("Nombre", max_length=80)
    slug = models.SlugField(
        "URL corta",
        max_length=90,
        unique=True,
        blank=True,
        help_text="Se genera del nombre. Se usa en ?plan=… para preseleccionar el plan.",
    )
    speed = models.CharField("Velocidad", max_length=60, blank=True, default="")
    price = models.CharField(
        "Precio (texto)", max_length=40, blank=True, default="", help_text="Ej: $499 al mes."
    )
    price_amount = models.DecimalField(
        "Precio (monto)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Solo si es un precio real. Si se define, el monto del pago "
            "se toma de aquí y no del cliente."
        ),
    )
    period = models.CharField("Periodo", max_length=20, default="/mes")
    tagline = models.CharField("Descripción corta", max_length=200, default="")
    features = models.JSONField(
        "Características",
        default=list,
        blank=True,
        help_text='Lista de textos. Ej: ["WiFi incluido", "Instalación gratis"]',
    )
    is_popular = models.BooleanField(
        "Destacado",
        default=False,
        help_text="Se muestra como 'Más popular'.",
    )
    url = models.CharField("Enlace (ancla o URL)", max_length=255, default="#contacto")
    order = models.PositiveIntegerField("Orden", default=0)
    active = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Plan residencial"
        verbose_name_plural = "Planes residenciales"

    @property
    def has_price(self):
        """True solo si el plan tiene un precio real definido."""
        return self.price_amount is not None

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "plan"
            slug = base
            index = 2
            while Plan.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{index}"
                index += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} — {self.speed}" if self.speed else self.name


class StoryStep(models.Model):
    """Paso de la escena fija (sección 'Qué hacemos')."""

    label = models.CharField("Etiqueta", max_length=120, default="01 · Internet dedicado")
    title = models.CharField("Título", max_length=200, default="Una conexión")
    title_highlight = models.CharField("Resaltado en degradado", max_length=120, default="tuya.")
    description = models.TextField("Descripción", max_length=400)
    visual_svg = models.TextField(
        "Visual SVG",
        blank=True,
        default="",
        help_text="Código SVG inline (solo administradores de confianza). Se usa si no hay Lottie.",
    )
    visual_lottie = models.CharField(
        "Visual Lottie (opcional)",
        max_length=120,
        blank=True,
        default="",
        help_text="Nombre del archivo en static/lottie/. Ej: step1-signal.json",
    )
    glow_color = models.CharField("Color de brillo", max_length=40, default="rgba(8,124,240,.5)")
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Paso de historia"
        verbose_name_plural = "Pasos de historia"

    def __str__(self):
        return f"{self.label}: {self.title}"


class Differentiator(models.Model):
    """Tarjeta de la sección 'Por qué INTERNETWORK'."""

    icon = models.CharField("Ícono (carácter)", max_length=8, default="◉")
    title = models.CharField("Título", max_length=120)
    text = models.TextField("Texto", max_length=300)
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Diferenciador"
        verbose_name_plural = "Diferenciadores"

    def __str__(self):
        return self.title


class LegalPage(models.Model):
    """Página legal: aviso de privacidad, términos, aviso legal, cookies."""

    title = models.CharField("Título", max_length=120)
    slug = models.SlugField("URL", max_length=120, unique=True)
    content = models.TextField(
        "Contenido",
        help_text="Texto plano: cada línea se renderiza como un párrafo.",
    )
    updated_at = models.DateTimeField("Última actualización", auto_now=True)
    order = models.PositiveIntegerField("Orden", default=0)
    active = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Página legal"
        verbose_name_plural = "Páginas legales"

    def get_absolute_url(self):
        return reverse("core:legal_page", kwargs={"slug": self.slug})

    @property
    def paragraphs(self):
        """Contenido partido en párrafos (una línea = un párrafo)."""
        return [line.strip() for line in self.content.splitlines() if line.strip()]

    def __str__(self):
        return self.title


class Payment(models.Model):
    """Pago registrado desde la página de pagos."""

    METHOD_CHOICES = [
        ("transfer", "Transferencia"),
        ("card", "Tarjeta"),
        ("cash", "Efectivo / OXXO"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("paid", "Pagado"),
    ]

    name = models.CharField("Nombre", max_length=150)
    email = models.EmailField("Correo")
    phone = models.CharField("Teléfono", max_length=40, blank=True, default="")
    service = models.CharField("Servicio o plan", max_length=150)
    amount = models.DecimalField("Monto", max_digits=10, decimal_places=2)
    method = models.CharField("Método", max_length=20, choices=METHOD_CHOICES)
    reference = models.CharField("Referencia", max_length=40, unique=True)
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField("Fecha", auto_now_add=True)
    ip_address = models.GenericIPAddressField("IP", blank=True, null=True)
    paid_at = models.DateTimeField("Confirmado el", blank=True, null=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Confirmado por",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    provider = models.CharField(
        "Pasarela",
        max_length=30,
        blank=True,
        default="",
        help_text="Pasarela que procesó el pago (ej: mercadopago).",
    )
    provider_ref = models.CharField("ID en la pasarela", max_length=120, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"{self.reference} — {self.service} ({self.get_status_display()})"


class UsedLoginToken(models.Model):
    """Nonce de un enlace mágico ya usado (garantiza un solo uso)."""

    nonce = models.CharField("Nonce", max_length=64, unique=True)
    email = models.EmailField("Correo", blank=True, default="")
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = "Token de acceso usado"
        verbose_name_plural = "Tokens de acceso usados"

    def __str__(self):
        return self.nonce


class Lead(models.Model):
    """Solicitud de contacto enviada desde el formulario."""

    STATUS_CHOICES = [
        ("new", "Nuevo"),
        ("contacted", "Contactado"),
        ("closed", "Cerrado"),
    ]

    name = models.CharField("Nombre", max_length=150)
    company = models.CharField("Empresa", max_length=150, blank=True, default="")
    email = models.EmailField("Correo")
    phone = models.CharField("Teléfono", max_length=40, blank=True, default="")
    service_of_interest = models.CharField("Servicio de interés", max_length=120)
    message = models.TextField("Mensaje", blank=True, default="")
    created_at = models.DateTimeField("Fecha", auto_now_add=True)
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default="new")
    ip_address = models.GenericIPAddressField("IP", blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"

    def __str__(self):
        return f"{self.name} — {self.service_of_interest} ({self.get_status_display()})"
