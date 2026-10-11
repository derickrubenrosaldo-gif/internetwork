"""Carga el contenido base del sitio.

Modos
-----
Sin opciones   Solo **crea lo que falta** (``get_or_create``): nunca
               sobrescribe lo que hayas editado en el admin.
``--force``    Sobrescribe el contenido existente con los valores base.
``--demo``     Añade además contenido de **EJEMPLO** (precios, cifras,
               cobertura y datos bancarios ficticios). No usar en producción.
``--reset``    Elimina el contenido base y lo vuelve a crear (destructivo).

Regla del proyecto: nada de datos inventados por defecto. Precios, cifras,
cobertura y datos bancarios solo se cargan con ``--demo``.
"""

from django.core.management.base import BaseCommand

from core.models import (
    Differentiator,
    Lead,
    LegalPage,
    Plan,
    Service,
    SiteConfig,
    StoryStep,
)

# --- Cobertura real: (localidad, municipio) ---------------------------------
COVERAGE_AREAS = [
    ("Allende", "Coatzacoalcos"),
    ("Mundo Nuevo", "Coatzacoalcos"),
    ("Colorado", "Coatzacoalcos"),
    ("Guillermo Prieto", "Coatzacoalcos"),
    ("Las Barrillas", "Coatzacoalcos"),
    ("Tonalá", "Agua Dulce"),
    ("El Muelle", "Agua Dulce"),
    ("Nanchital", "Nanchital"),
    ("Pollo de Oro", "Nanchital"),
    ("Ixhuatlán del Sureste", "Ixhuatlán del Sureste"),
    ("El Chapo", "Ixhuatlán del Sureste"),
    ("Villa Cuichapa", "Moloacán"),
    ("Moloacán", "Moloacán"),
    ("Mapachapa", "Minatitlán"),
    ("Capoacán", "Minatitlán"),
    ("Nuevo Atoyac", "Minatitlán"),
    ("Francita", "Minatitlán"),
    ("Coacotla", "Cosoleacaque"),
    ("San Pedro Mártir", "Cosoleacaque"),
    ("Estero del Pantano", "Cosoleacaque"),
    ("Jáltipan", "Jáltipan"),
    ("Lomas de Tacamichapan", "Jáltipan"),
    ("Chinameca", "Chinameca"),
    ("Chacalapa", "Chinameca"),
    ("Oteapan", "Oteapan"),
    ("Congregación Hidalgo", "Acayucan"),
    ("Dehesa", "Acayucan"),
    ("Comején", "Acayucan"),
    ("Michapan de Osorio", "Acayucan"),
    ("Soconusco", "Soconusco"),
    ("Chogota", "Soconusco"),
    ("Oluta", "Oluta"),
    ("Correa", "Oluta"),
    ("Sayula de Alemán", "Sayula de Alemán"),
    ("Aguilera", "Sayula de Alemán"),
    ("Almagres", "Sayula de Alemán"),
    ("Texistepec", "Texistepec"),
    ("San Lorenzo Tenochtitlán", "Texistepec"),
    ("Villa Juanita", "San Juan Evangelista"),
    ("La Lima", "San Juan Evangelista"),
    ("Achotal", "San Juan Evangelista"),
    ("Las Choapas", "Las Choapas"),
    ("Cerro de Nanchital", "Las Choapas"),
    ("Río Playas", "Las Choapas"),
    ("La Chinantla", "Uxpanapa"),
    ("Poblado Uno", "Uxpanapa"),
    ("Poblado Dos", "Uxpanapa"),
    ("Poblado Diez", "Uxpanapa"),
    ("Hidalgotitlán", "Hidalgotitlán"),
    ("El Arrozal", "Hidalgotitlán"),
    ("Jesús Carranza", "Jesús Carranza"),
    ("Suchilapan del Río", "Jesús Carranza"),
    ("Sihuapan", "San Andrés Tuxtla"),
    ("Comoapan", "San Andrés Tuxtla"),
    ("Calería", "San Andrés Tuxtla"),
    ("Salto de Eyipantla", "San Andrés Tuxtla"),
    ("Tilapan", "San Andrés Tuxtla"),
    ("Sontecomapan", "Catemaco"),
    ("La Victoria", "Catemaco"),
    ("Coyame", "Catemaco"),
    ("Tebanca", "Catemaco"),
    ("Tres Zapotes", "Santiago Tuxtla"),
    ("Tlapacoyan", "Santiago Tuxtla"),
    ("Tapalapan", "Santiago Tuxtla"),
    ("Juan Díaz Covarrubias", "Hueyapan de Ocampo"),
    ("Cuatotolapan", "Hueyapan de Ocampo"),
    ("Los Mangos", "Hueyapan de Ocampo"),
    ("Tecolapan", "Ángel R. Cabada"),
    ("El Porvenir", "Ángel R. Cabada"),
]


def _coverage_text():
    """Serializa la cobertura como "Localidad — Municipio" (una por línea)."""
    return "\n".join(f"{locality} — {municipality}" for locality, municipality in COVERAGE_AREAS)


# --- Configuración base (datos reales del negocio) ---------------------------
BASE_SITE_CONFIG = {
    "email": "",
    "phone": "9211200027",
    "whatsapp": "9211200027",
    "address": "Minatitlán, Veracruz",
    "coverage_zones": _coverage_text(),
    "hero_eyebrow": "Conectando tu mundo",
    "hero_title": "Internet sin",
    "hero_title_highlight": "límites.",
    "hero_subtitle": (
        "Internet dedicado, soluciones IT, infraestructura y software. "
        "Llegamos hasta donde otros no llegan."
    ),
    "statement_text": (
        "Somos INTERNETWORK. Una sola empresa para conectar tu negocio, "
        "tu comunidad y tu hogar, con la tecnología que necesitas para crecer."
    ),
    "rural_title": "La distancia no debería limitar tus",
    "rural_title_highlight": "oportunidades.",
    "rural_description": (
        "Acercamos servicios digitales a comunidades rurales, comercios, "
        "instituciones y hogares que necesitan estar conectados."
    ),
    "stats": [],
    "socials": [],
    "dedicated_title": "Ancho de banda exclusivo para tu operación.",
    "dedicated_title_highlight": "Sin compartir.",
    "dedicated_description": (
        "El internet dedicado te asigna una conexión privada y simétrica: "
        "toda la capacidad es para tu negocio, con monitoreo continuo."
    ),
    "dedicated_features": [
        {
            "title": "Ancho de banda garantizado",
            "text": "Velocidad simétrica y exclusiva, sin compartir con otros usuarios.",
        },
        {
            "title": "Latencia mínima",
            "text": "Enrutamiento directo para videollamadas, VPN y sistemas en la nube.",
        },
        {
            "title": "IP fija pública",
            "text": "Dirección estática para servidores, cámaras y accesos remotos.",
        },
        {
            "title": "Fibra propia",
            "text": "Red de última milla propia: sin terceros entre nosotros y tu oficina.",
        },
        {
            "title": "Soporte prioritario",
            "text": "Atención de ingeniería con seguimiento de tu caso.",
        },
    ],
    # Cuenta real para transferencias (banco Revolut).
    "payment_instructions": (
        "Revolut — Cuenta: 64699040406103622. En tu transferencia usa la "
        "referencia que te asignamos al registrar el pago."
    ),
}

# --- Contenido de EJEMPLO (solo con --demo) ---------------------------------
# Solo lo que sigue sin dato real: las cifras de la banda de resultados.
DEMO_SITE_CONFIG = {
    "stats": [
        {"value": "+500", "label": "Negocios conectados"},
        {"value": "99.9%", "label": "Estabilidad de enlaces"},
        {"value": "24/7", "label": "Soporte técnico"},
        {"value": "+50", "label": "Zonas rurales"},
    ],
}

DEMO_PLANS = [
    {
        "name": "Esencial (ejemplo)",
        "speed": "100 Mbps",
        "price": "$299",
        "price_amount": "299.00",
        "period": "/mes",
        "tagline": "Plan de ejemplo. Sustituye el precio por el real.",
        "features": ["WiFi incluido", "Instalación incluida", "Soporte técnico"],
        "is_popular": False,
        "url": "#contacto",
        "order": 0,
    },
    {
        "name": "Familiar (ejemplo)",
        "speed": "300 Mbps",
        "price": "$499",
        "price_amount": "499.00",
        "period": "/mes",
        "tagline": "Plan de ejemplo. Sustituye el precio por el real.",
        "features": ["Router WiFi 6", "Hasta 10 dispositivos", "Soporte prioritario"],
        "is_popular": True,
        "url": "#contacto",
        "order": 1,
    },
]

# --- Planes reales ------------------------------------------------------------
# Nombre, precio y velocidad son los datos del negocio. Sin "Más popular" (no es
# un dato real) y sin características inventadas: se editan desde el admin.
PLANS = [
    {
        "name": "15 Megas",
        "speed": "15 Mbps",
        "price": "$380",
        "price_amount": "380.00",
        "period": "/mes",
        "tagline": "",
        "features": [],
        "is_popular": False,
        "url": "#contacto",
        "order": 0,
    },
    {
        "name": "30 Megas",
        "speed": "30 Mbps",
        "price": "$480",
        "price_amount": "480.00",
        "period": "/mes",
        "tagline": "",
        "features": [],
        "is_popular": False,
        "url": "#contacto",
        "order": 1,
    },
    {
        "name": "100 Megas",
        "speed": "100 Mbps",
        "price": "$600",
        "price_amount": "600.00",
        "period": "/mes",
        "tagline": "",
        "features": [],
        "is_popular": False,
        "url": "#contacto",
        "order": 2,
    },
]

SERVICES = [
    {
        "title": "Internet dedicado",
        "description": "Conectividad de alto rendimiento para operaciones que exigen estabilidad y capacidad.",
        "icon": "⌁",
        "lottie_file": "signal.json",
        "url": "#dedicado",
        "link_text": "Conocer el servicio",
        "order": 0,
    },
    {
        "title": "Soluciones IT",
        "description": "Asesoría, soporte, mantenimiento, seguridad y administración de sistemas.",
        "icon": "☁",
        "lottie_file": "dashboard.json",
        "url": "#contacto",
        "link_text": "Conocer el servicio",
        "order": 1,
    },
    {
        "title": "Conectividad rural",
        "description": "Alternativas de internet para localidades y comunidades alejadas.",
        "icon": "♧",
        "lottie_file": "mountain.json",
        "url": "#rural",
        "link_text": "Conocer el servicio",
        "order": 2,
    },
    {
        "title": "Infraestructura",
        "description": "Diseño e implementación de redes, cableado, servidores y soluciones a tu medida.",
        "icon": "▤",
        "lottie_file": "",
        "url": "#contacto",
        "link_text": "Conocer el servicio",
        "order": 3,
    },
    {
        "title": "Desarrollo de software",
        "description": "Aplicaciones, automatización y sistemas personalizados para tus procesos.",
        "icon": "</>",
        "lottie_file": "code.json",
        "url": "#contacto",
        "link_text": "Conocer el servicio",
        "order": 4,
    },
    {
        "title": "Páginas web",
        "description": "Sitios modernos, rápidos y adaptables para presentar tu marca y captar clientes.",
        "icon": "▣",
        "lottie_file": "",
        "url": "#contacto",
        "link_text": "Conocer el servicio",
        "order": 5,
    },
]

STORY_STEPS = [
    {
        "label": "Internet dedicado",
        "title": "Una conexión",
        "title_highlight": "tuya.",
        "description": "Enlaces estables y de alto rendimiento para empresas y organizaciones que no pueden darse el lujo de desconectarse.",
        "visual_lottie": "step1-signal.json",
        "visual_svg": '<svg class="vis" viewBox="0 0 200 200" fill="none" stroke="#0a7cbe" stroke-width="3"><circle cx="100" cy="100" r="22"/><circle cx="100" cy="100" r="52" opacity=".6"/><circle cx="100" cy="100" r="82" opacity=".3"/><path d="M100 78V18M100 182v-60M78 100H18M182 100h-60" stroke-linecap="round"/><circle cx="100" cy="100" r="8" fill="#0a7cbe"/></svg>',
        "glow_color": "rgba(11,99,214,.45)",
        "order": 0,
    },
    {
        "label": "Soluciones IT",
        "title": "Tu tecnología,",
        "title_highlight": "en orden.",
        "description": "Redes, seguridad, soporte y administración de sistemas para que tu operación funcione sin sobresaltos.",
        "visual_lottie": "step2-dashboard.json",
        "visual_svg": '<svg class="vis" viewBox="0 0 200 200" fill="none" stroke="#0a7cbe" stroke-width="3"><rect x="30" y="40" width="140" height="90" rx="12"/><path d="M70 170h60M100 130v40" stroke-linecap="round"/><path d="M60 85l20 20 20-30 30 35" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        "glow_color": "rgba(10,162,223,.35)",
        "order": 1,
    },
    {
        "label": "Zonas rurales",
        "title": "Llegamos",
        "title_highlight": "más lejos.",
        "description": "Conectividad para comunidades y localidades de difícil acceso, porque la distancia no debe limitar oportunidades.",
        "visual_lottie": "step3-mountain.json",
        "visual_svg": '<svg class="vis" viewBox="0 0 200 200" fill="none" stroke="#0a7cbe" stroke-width="3" stroke-linecap="round"><path d="M100 170V90"/><path d="M100 90c-30-6-46-30-46-50 26 0 46 18 46 50zM100 90c30-6 46-30 46-50-26 0-46 18-46 50z" opacity=".85"/><path d="M58 170h84" /><path d="M60 128c24-30 56-30 80 0" opacity=".5"/><path d="M40 108c38-50 82-50 120 0" opacity=".3"/></svg>',
        "glow_color": "rgba(30,120,220,.35)",
        "order": 2,
    },
    {
        "label": "Software y web",
        "title": "Lo construimos",
        "title_highlight": "a tu medida.",
        "description": "Sistemas, aplicaciones y páginas web desarrolladas para tu negocio, desde la infraestructura hasta la pantalla.",
        "visual_lottie": "step4-code.json",
        "visual_svg": '<svg class="vis" viewBox="0 0 200 200" fill="none" stroke="#0a7cbe" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M72 62L28 100l44 38M128 62l44 38-44 38"/><path d="M114 44L86 156" opacity=".8"/></svg>',
        "glow_color": "rgba(11,80,200,.35)",
        "order": 3,
    },
]

DIFFERENTIATORS = [
    {
        "icon": "◉",
        "title": "A tu medida",
        "text": "Propuestas adaptadas a tus objetivos, ubicación y necesidades técnicas.",
        "order": 0,
    },
    {
        "icon": "↗",
        "title": "Enfoque en resultados",
        "text": "Tecnología pensada para la continuidad y el crecimiento de tu operación.",
        "order": 1,
    },
    {
        "icon": "⌘",
        "title": "Un solo aliado",
        "text": "Internet, infraestructura, software y web bajo una misma marca.",
        "order": 2,
    },
    {
        "icon": "♡",
        "title": "Cercanía y soporte",
        "text": "Te orientamos antes, durante y después de implementar tu solución.",
        "order": 3,
    },
]

# Borradores legales: sustituir por el texto revisado por un abogado.
LEGAL_PAGES = [
    {
        "title": "Aviso de privacidad",
        "slug": "aviso-de-privacidad",
        "order": 0,
        "content": """BORRADOR PARA REVISIÓN DE UN ABOGADO. En INTERNETWORK respetamos tu privacidad. Este aviso describe cómo tratamos tus datos personales cuando usas el sitio, nos escribes o registras un pago.
Responsable: INTERNETWORK, con domicilio en Minatitlán, Veracruz, México. Teléfono y WhatsApp: 9211200027. Falta completar la dirección exacta (calle y número) antes de publicar.
Datos que tratamos: nombre, correo, teléfono, empresa y mensaje (contacto); nombre, correo, teléfono, servicio y monto (pagos); y los pagos asociados a tu correo cuando consultas el panel de clientes.
Finalidades primarias: atender tu solicitud, registrar y confirmar tu pago, dar seguimiento a la relación comercial y cumplir obligaciones legales.
Finalidades secundarias: enviarte información sobre nuestros servicios. Puedes oponerte sin afectar la relación principal.
Derechos ARCO: puedes acceder, rectificar, cancelar u oponerte al tratamiento de tus datos, así como revocar tu consentimiento, escribiendo al teléfono o WhatsApp de contacto.
Transferencias: no transferimos tus datos a terceros salvo a los proveedores necesarios para operar el sitio y procesar pagos, o cuando la ley lo exija.
Conservación: conservamos tus datos mientras exista la relación comercial y el tiempo necesario para cumplir obligaciones legales.
Cambios: este aviso puede actualizarse. Publicaremos la versión vigente en este sitio.""",
    },
    {
        "title": "Términos y condiciones",
        "slug": "terminos-y-condiciones",
        "order": 1,
        "content": """BORRADOR PARA REVISIÓN DE UN ABOGADO. Estos términos regulan el uso del sitio de INTERNETWORK y la contratación de sus servicios.
Servicios: internet dedicado, conectividad rural, soluciones IT, infraestructura, desarrollo de software y páginas web, conforme a la propuesta contratada.
Obligaciones del usuario: proporcionar información veraz, usar los servicios de forma lícita y no interferir con la red ni la infraestructura.
Disponibilidad: procuramos la continuidad del servicio. Los compromisos de nivel de servicio se establecen por escrito en cada propuesta.
Pagos: los montos se confirman en la propuesta o contrato correspondiente.
Propiedad intelectual: el contenido, diseños, logotipos y software del sitio pertenecen a INTERNETWORK o a sus licenciantes.
Ley aplicable: estos términos se rigen por la legislación aplicable en el domicilio del responsable.""",
    },
    {
        "title": "Aviso legal",
        "slug": "aviso-legal",
        "order": 2,
        "content": """BORRADOR PARA REVISIÓN DE UN ABOGADO. Este aviso legal regula el uso del sitio de INTERNETWORK.
Titular: INTERNETWORK. Los datos completos de contacto deben publicarse antes de entrar en operación.
Objeto: el sitio informa sobre los servicios de INTERNETWORK y permite enviar solicitudes y registrar pagos.
Responsabilidad del usuario: el usuario asume el uso lícito del sitio y la veracidad de la información que proporciona.
Propiedad intelectual: queda prohibida la reproducción total o parcial de los contenidos sin autorización por escrito.
Enlaces de terceros: no nos responsabilizamos del contenido de sitios externos enlazados.
Modificaciones: podemos modificar el sitio, sus servicios y este aviso.""",
    },
    {
        "title": "Política de cookies",
        "slug": "politica-de-cookies",
        "order": 3,
        "content": """BORRADOR PARA REVISIÓN DE UN ABOGADO. Este sitio usa únicamente cookies técnicas necesarias para su funcionamiento.
Cookies técnicas: mantienen la sesión del panel de clientes y protegen los formularios contra falsificaciones. No se pueden desactivar sin afectar el funcionamiento.
Analítica: este sitio no instala cookies de analítica ni de publicidad. Si en el futuro se añaden, se actualizará esta política y se pedirá consentimiento.
Cómo desactivarlas: puedes eliminar o bloquear cookies desde la configuración de tu navegador.""",
    },
]


class Command(BaseCommand):
    help = "Carga el contenido base del sitio (no sobrescribe lo editado en el admin)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sobrescribe el contenido existente con los valores base.",
        )
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Carga además contenido de EJEMPLO (precios, cifras y datos bancarios ficticios).",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina el contenido base y lo vuelve a crear (destructivo; implica --force).",
        )

    def handle(self, *args, **options):
        force = options["force"] or options["reset"]
        demo = options["demo"]

        if options["reset"]:
            Service.objects.all().delete()
            Plan.objects.all().delete()
            StoryStep.objects.all().delete()
            Differentiator.objects.all().delete()
            LegalPage.objects.all().delete()
            self.stdout.write(self.style.WARNING("Contenido anterior eliminado (--reset)."))

        config_values = dict(BASE_SITE_CONFIG)
        if demo:
            config_values.update(DEMO_SITE_CONFIG)

        if force:
            SiteConfig.objects.update_or_create(pk=1, defaults=config_values)
        else:
            SiteConfig.objects.get_or_create(pk=1, defaults=config_values)

        self._load(Service, SERVICES, "title", force)
        self._load(LegalPage, LEGAL_PAGES, "slug", force)
        self._load(StoryStep, STORY_STEPS, "label", force)
        self._load(Differentiator, DIFFERENTIATORS, "title", force)
        self._load(Plan, PLANS, "name", force)
        if demo:
            self._load(Plan, DEMO_PLANS, "name", force)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completado: {Service.objects.count()} servicios, "
                f"{Plan.objects.count()} planes, "
                f"{LegalPage.objects.count()} páginas legales, "
                f"{StoryStep.objects.count()} pasos, "
                f"{Differentiator.objects.count()} diferenciadores."
            )
        )
        if demo:
            self.stdout.write(
                self.style.WARNING(
                    "Modo --demo: se cargaron precios, cifras, cobertura y datos "
                    "bancarios FICTICIOS. No los publiques; sustitúyelos por los reales."
                )
            )
        if not Lead.objects.exists():
            self.stdout.write("No hay solicitudes (Lead) en la base de datos.")

    @staticmethod
    def _load(model, items, key, force):
        """Crea lo que falta; con ``force`` sobrescribe lo existente."""
        for item in items:
            lookup = {key: item[key]}
            if force:
                model.objects.update_or_create(**lookup, defaults=item)
            else:
                model.objects.get_or_create(**lookup, defaults=item)
