"""Carga el contenido original de internetwork-scroll.html en la base de datos."""

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

SITE_CONFIG = {
    "email": "contacto@tudominio.com",
    "phone": "",
    "whatsapp": "",
    "address": "",
    "coverage_zones": "Ciudad de México, Guadalajara, Monterrey, Puebla",
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
    "stats": [
        {"value": "+500", "label": "Negocios conectados"},
        {"value": "99.9%", "label": "Estabilidad de enlaces"},
        {"value": "24/7", "label": "Soporte técnico"},
        {"value": "+50", "label": "Zonas rurales"},
    ],
    "socials": [],
    "dedicated_title": "Ancho de banda exclusivo para tu operación.",
    "dedicated_title_highlight": "Sin compartir.",
    "dedicated_description": (
        "El internet dedicado te asigna una conexión privada y simétrica: "
        "toda la capacidad es para tu negocio, con respuesta garantizada "
        "y monitoreo continuo."
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
            "title": "SLA de 99.9%",
            "text": "Compromiso por escrito, con monitoreo proactivo las 24 horas.",
        },
        {
            "title": "Fibra propia",
            "text": "Red de última milla propia: sin terceros entre nosotros y tu oficina.",
        },
        {
            "title": "Soporte prioritario",
            "text": "Ingeniero asignado y respuesta garantizada en minutos.",
        },
    ],
    "payment_instructions": (
        "Banco Ejemplo, Cuenta: 0123456789, CLABE interbancaria: "
        "012180001234567890. En tu transferencia usa la referencia "
        "que te asignamos al registrar el pago. También aceptamos "
        "pagos con enlace de tarjeta y en tiendas de conveniencia."
    ),
}

SERVICES = [
    {
        "title": "Internet dedicado",
        "description": "Conectividad de alto rendimiento para operaciones que exigen estabilidad y capacidad.",
        "icon": "⌁",
        "lottie_file": "signal.json",
        "url": "#dedicado",
        "link_text": "Solicitar información",
        "order": 0,
    },
    {
        "title": "Soluciones IT",
        "description": "Asesoría, soporte, mantenimiento, seguridad y administración de sistemas.",
        "icon": "☁",
        "lottie_file": "dashboard.json",
        "url": "#contacto",
        "link_text": "Conoce más",
        "order": 1,
    },
    {
        "title": "Conectividad rural",
        "description": "Alternativas de internet para localidades y comunidades alejadas.",
        "icon": "♧",
        "lottie_file": "mountain.json",
        "url": "#rural",
        "link_text": "Ver propuesta",
        "order": 2,
    },
    {
        "title": "Infraestructura",
        "description": "Diseño e implementación de redes, cableado, servidores y soluciones a tu medida.",
        "icon": "▤",
        "lottie_file": "",
        "url": "#contacto",
        "link_text": "Hablemos",
        "order": 3,
    },
    {
        "title": "Desarrollo de software",
        "description": "Aplicaciones, automatización y sistemas personalizados para tus procesos.",
        "icon": "</>",
        "lottie_file": "code.json",
        "url": "#contacto",
        "link_text": "Desarrolla tu proyecto",
        "order": 4,
    },
    {
        "title": "Páginas web",
        "description": "Sitios modernos, rápidos y adaptables para presentar tu marca y captar clientes.",
        "icon": "▣",
        "lottie_file": "",
        "url": "#contacto",
        "link_text": "Crea tu página",
        "order": 5,
    },
]

PLANS = [
    {
        "name": "Esencial",
        "speed": "100 Mbps",
        "price": "$299",
        "period": "/mes",
        "tagline": "Para empezar a conectar tu casa sin complicaciones.",
        "features": [
            "WiFi incluido",
            "Instalación gratis",
            "Soporte técnico 24/7",
            "Ideal para 1 a 3 dispositivos",
        ],
        "is_popular": False,
        "url": "#contacto",
        "order": 0,
    },
    {
        "name": "Familiar",
        "speed": "300 Mbps",
        "price": "$499",
        "period": "/mes",
        "tagline": "El equilibrio perfecto: velocidad y precio para toda la casa.",
        "features": [
            "Todo lo del plan Esencial",
            "Hasta 10 dispositivos",
            "Router WiFi 6",
            "Prioridad en soporte técnico",
            "Streaming y videollamadas sin cortes",
        ],
        "is_popular": True,
        "url": "#contacto",
        "order": 1,
    },
    {
        "name": "Turbo",
        "speed": "600 Mbps",
        "price": "$799",
        "period": "/mes",
        "tagline": "Máxima velocidad para hogares conectados y teletrabajo pesado.",
        "features": [
            "Todo lo del plan Familiar",
            "Hasta 20 dispositivos",
            "IP fija opcional",
            "Instalación prioritaria",
            "Asesoría de red incluida",
        ],
        "is_popular": False,
        "url": "#contacto",
        "order": 2,
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


LEGAL_PAGES = [
    {
        "title": "Aviso de privacidad",
        "slug": "aviso-de-privacidad",
        "order": 0,
        "content": """En INTERNETWORK respetamos tu privacidad. Este aviso describe cómo recopilamos, usamos y protegemos tus datos personales cuando usas nuestro sitio web o te comunicas con nosotros.
Somos INTERNETWORK, responsable del tratamiento de tus datos. Puedes contactarnos a través del formulario de contacto o del correo indicado en la sección de contacto.
¿Qué datos recopilamos? Cuando envías el formulario de contacto recopilamos: nombre, correo electrónico, empresa, teléfono y mensaje. También guardamos tu dirección IP y la fecha de envío por seguridad.
¿Para qué usamos tus datos? Para atender tu solicitud, enviarte información sobre nuestros servicios, gestionar la relación comercial y cumplir obligaciones legales.
Base legal: el tratamiento se basa en tu consentimiento al enviar el formulario y en la ejecución de la relación contractual.
Tus derechos: puedes acceder, rectificar, cancelar u oponerte al tratamiento de tus datos, así como solicitar su portabilidad. Ejerce tus derechos escribiendo al correo de contacto.
Cookies: usamos cookies técnicas esenciales y analíticas anónimas. Consulta nuestra Política de cookies para más detalle.
Conservación: tus datos se conservan mientras dure la relación comercial y el tiempo necesario para cumplir obligaciones legales.
Cambios: este aviso puede actualizarse. La versión vigente es la que aparece en nuestro sitio.""",
    },
    {
        "title": "Términos y condiciones",
        "slug": "terminos-y-condiciones",
        "order": 1,
        "content": """Estos términos regulan el uso del sitio web de INTERNETWORK y la contratación de sus servicios. Al usar el sitio o contratar un servicio, aceptas estos términos.
Servicios: ofrecemos internet dedicado, conectividad rural, soluciones IT, infraestructura, desarrollo de software y páginas web, conforme a las propuestas y planes publicados en el sitio.
Obligaciones del usuario: proporcionar información veraz, usar los servicios de forma lícita y no interferir con la red ni la infraestructura de INTERNETWORK.
Disponibilidad: procuramos la continuidad del servicio. Los planes y proyectos pueden incluir compromisos de estabilidad (SLA) según la propuesta contratada.
Pagos: los precios mostrados son referenciales y se confirman en la propuesta o contrato correspondiente.
Propiedad intelectual: el contenido, diseños, logotipos y software del sitio son propiedad de INTERNETWORK o de sus licenciantes.
Responsabilidad: INTERNETWORK no se hace responsable de daños indirectos ni de la indisponibilidad temporal del sitio, salvo lo establecido en la ley aplicable.
Ley aplicable: estos términos se rigen por la legislación del país donde opera INTERNETWORK.""",
    },
    {
        "title": "Aviso legal",
        "slug": "aviso-legal",
        "order": 2,
        "content": """El presente aviso legal regula el uso del sitio web de INTERNETWORK (en adelante, el sitio).
Titular: INTERNETWORK. La información de contacto completa está disponible en la sección de contacto del sitio.
Objeto: el sitio informa sobre los servicios de INTERNETWORK y permite enviar solicitudes de información a través del formulario de contacto.
Responsabilidad del usuario: el usuario asume el uso lícito del sitio y la veracidad de la información que proporciona.
Propiedad intelectual e industrial: todos los contenidos del sitio están protegidos. Queda prohibida su reproducción total o parcial sin autorización por escrito.
Enlaces de terceros: el sitio puede incluir enlaces externos sobre cuyo contenido INTERNETWORK no se responsabiliza.
Modificaciones: INTERNETWORK se reserva el derecho de modificar el sitio, sus servicios y el presente aviso sin previo aviso.""",
    },
    {
        "title": "Política de cookies",
        "slug": "politica-de-cookies",
        "order": 3,
        "content": """Las cookies son pequeños archivos que el sitio guarda en tu navegador para recordar tus preferencias y mejorar la experiencia de navegación.
Cookies técnicas: esenciales para el funcionamiento del sitio (sesión, idioma y seguridad). No se pueden desactivar.
Cookies analíticas: permiten conocer de forma anónima cómo navegan los visitantes para mejorar el sitio. No identifican a personas.
Terceros: podemos usar servicios de analítica que instalan sus propias cookies bajo sus propias políticas de privacidad.
Cómo desactivarlas: puedes eliminar o bloquear cookies desde la configuración de tu navegador. Desactivarlas puede afectar algunas funciones del sitio.
Al seguir navegando entendemos que aceptas el uso de cookies. Puedes revocar tu consentimiento en cualquier momento desde tu navegador.""",
    },
]


class Command(BaseCommand):
    help = "Carga el contenido de demostración del sitio (equivalente al HTML original)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina servicios, pasos y diferenciadores existentes antes de cargar.",
        )

    def handle(self, *args, **options):
        SiteConfig.objects.update_or_create(
            pk=1, defaults={k: v for k, v in SITE_CONFIG.items()}
        )
        self.stdout.write(self.style.SUCCESS("Configuración del sitio actualizada."))

        if options["reset"]:
            Service.objects.all().delete()
            Plan.objects.all().delete()
            StoryStep.objects.all().delete()
            Differentiator.objects.all().delete()
            LegalPage.objects.all().delete()

        for item in SERVICES:
            Service.objects.update_or_create(title=item["title"], defaults=item)
        for item in PLANS:
            Plan.objects.update_or_create(name=item["name"], defaults=item)
        for item in LEGAL_PAGES:
            LegalPage.objects.update_or_create(slug=item["slug"], defaults=item)
        for item in STORY_STEPS:
            StoryStep.objects.update_or_create(label=item["label"], defaults=item)
        for item in DIFFERENTIATORS:
            Differentiator.objects.update_or_create(title=item["title"], defaults=item)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completado: {Service.objects.count()} servicios, "
                f"{Plan.objects.count()} planes residenciales, "
                f"{LegalPage.objects.count()} páginas legales, "
                f"{StoryStep.objects.count()} pasos de historia, "
                f"{Differentiator.objects.count()} diferenciadores."
            )
        )
        if not Lead.objects.exists():
            self.stdout.write(self.style.WARNING("No hay solicitudes (Lead) en la base de datos."))
