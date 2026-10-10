"""Modelos del sitio INTERNETWORK — todo editable desde el admin."""

from django.db import models


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
    def zones_list(self):
        return [z.strip() for z in self.coverage_zones.split(",") if z.strip()]

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
