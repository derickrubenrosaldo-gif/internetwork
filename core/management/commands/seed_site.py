"""Carga el contenido original de internetwork-scroll.html en la base de datos."""

from django.core.management.base import BaseCommand

from core.models import Differentiator, Lead, Service, SiteConfig, StoryStep

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
}

SERVICES = [
    {
        "title": "Internet dedicado",
        "description": "Conectividad de alto rendimiento para operaciones que exigen estabilidad y capacidad.",
        "icon": "⌁",
        "lottie_file": "signal.json",
        "url": "#contacto",
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

STORY_STEPS = [
    {
        "label": "01 · Internet dedicado",
        "title": "Una conexión",
        "title_highlight": "tuya.",
        "description": "Enlaces estables y de alto rendimiento para empresas y organizaciones que no pueden darse el lujo de desconectarse.",
        "visual_lottie": "step1-signal.json",
        "visual_svg": '<svg class="vis" viewBox="0 0 200 200" fill="none" stroke="#27c4ff" stroke-width="3"><circle cx="100" cy="100" r="22"/><circle cx="100" cy="100" r="52" opacity=".6"/><circle cx="100" cy="100" r="82" opacity=".3"/><path d="M100 78V18M100 182v-60M78 100H18M182 100h-60" stroke-linecap="round"/><circle cx="100" cy="100" r="8" fill="#27c4ff"/></svg>',
        "glow_color": "rgba(8,124,240,.5)",
        "order": 0,
    },
    {
        "label": "02 · Soluciones IT",
        "title": "Tu tecnología,",
        "title_highlight": "en orden.",
        "description": "Redes, seguridad, soporte y administración de sistemas para que tu operación funcione sin sobresaltos.",
        "visual_lottie": "step2-dashboard.json",
        "visual_svg": '<svg class="vis" viewBox="0 0 200 200" fill="none" stroke="#27c4ff" stroke-width="3"><rect x="30" y="40" width="140" height="90" rx="12"/><path d="M70 170h60M100 130v40" stroke-linecap="round"/><path d="M60 85l20 20 20-30 30 35" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        "glow_color": "rgba(39,196,255,.4)",
        "order": 1,
    },
    {
        "label": "03 · Zonas rurales",
        "title": "Llegamos",
        "title_highlight": "más lejos.",
        "description": "Conectividad para comunidades y localidades de difícil acceso, porque la distancia no debe limitar oportunidades.",
        "visual_lottie": "step3-mountain.json",
        "visual_svg": '<svg class="vis" viewBox="0 0 200 200" fill="none" stroke="#27c4ff" stroke-width="3" stroke-linecap="round"><path d="M100 170V90"/><path d="M100 90c-30-6-46-30-46-50 26 0 46 18 46 50zM100 90c30-6 46-30 46-50-26 0-46 18-46 50z" opacity=".85"/><path d="M58 170h84" /><path d="M60 128c24-30 56-30 80 0" opacity=".5"/><path d="M40 108c38-50 82-50 120 0" opacity=".3"/></svg>',
        "glow_color": "rgba(20,200,150,.38)",
        "order": 2,
    },
    {
        "label": "04 · Software y web",
        "title": "Lo construimos",
        "title_highlight": "a tu medida.",
        "description": "Sistemas, aplicaciones y páginas web desarrolladas para tu negocio, desde la infraestructura hasta la pantalla.",
        "visual_lottie": "step4-code.json",
        "visual_svg": '<svg class="vis" viewBox="0 0 200 200" fill="none" stroke="#27c4ff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M72 62L28 100l44 38M128 62l44 38-44 38"/><path d="M114 44L86 156" opacity=".8"/></svg>',
        "glow_color": "rgba(130,90,255,.4)",
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
            StoryStep.objects.all().delete()
            Differentiator.objects.all().delete()

        for item in SERVICES:
            Service.objects.update_or_create(title=item["title"], defaults=item)
        for item in STORY_STEPS:
            StoryStep.objects.update_or_create(label=item["label"], defaults=item)
        for item in DIFFERENTIATORS:
            Differentiator.objects.update_or_create(title=item["title"], defaults=item)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completado: {Service.objects.count()} servicios, "
                f"{StoryStep.objects.count()} pasos de historia, "
                f"{Differentiator.objects.count()} diferenciadores."
            )
        )
        if not Lead.objects.exists():
            self.stdout.write(self.style.WARNING("No hay solicitudes (Lead) en la base de datos."))
