# INTERNETWORK — sitio web

Sitio de producción para **INTERNETWORK** (ISP de internet dedicado, soluciones IT,
conectividad en zonas rurales, desarrollo de software, infraestructura y páginas web).
Django 5 + frontend modular empaquetado con esbuild y animado con GSAP, Lenis,
Three.js y Lottie.

## Requisitos

- Python 3.12+ (3.13 probado)
- Node.js 20+ (22 probado)
- PostgreSQL para producción (SQLite para desarrollo)

## Instalación local (un comando)

```bash
python3 -m venv .venv && . .venv/bin/activate \
  && pip install -r requirements.txt \
  && npm install --include=dev \
  && npm run build \
  && python manage.py migrate \
  && python manage.py seed_site \
  && python manage.py runserver
```

Luego abre <http://localhost:8000>.

> Nota: en este entorno npm ignora devDependencies por defecto,
> por eso `--include=dev`.

## Desarrollo con watch

```bash
npm run dev    # esbuild en watch: JS (con code-splitting) y CSS
```

En otra terminal:

```bash
python manage.py runserver
```

Los fuentes del frontend viven en `frontend/` y el resultado del build en
`static/js/dist/` y `static/css/dist/` (se cargan con `{% static %}`).

## Variables de entorno

Copia `.env.example` a `.env` y ajusta:

| Variable | Descripción |
| --- | --- |
| `SECRET_KEY` | Clave secreta de Django (genera una larga y aleatoria) |
| `DEBUG` | `True` en desarrollo, `False` en producción |
| `ALLOWED_HOSTS` | Dominios permitidos, separados por coma |
| `DATABASE_URL` | `sqlite:///db.sqlite3` o `postgres://user:pass@host:5432/db` |
| `CACHE_URL` | Opcional, p. ej. `redis://localhost:6379/0` (si no, memoria local) |
| `CONTACT_EMAIL` | Correo que recibe las solicitudes del formulario |
| `WHATSAPP_NUMBER` | Número de WhatsApp (código de país + número, sin `+`) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` | Correo saliente (notificación de leads) |
| `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_SECONDS` | Anti-spam por IP (default 5/60s) |

## Base de datos y contenido

```bash
python manage.py migrate          # crea tablas
python manage.py seed_site        # carga el contenido del HTML original
python manage.py createsuperuser  # accede a /admin y edita todo el contenido
```

Todo el contenido (textos, servicios, pasos de la historia, diferenciadores,
contacto, redes) se edita desde el admin en `/admin`.

## Pruebas y calidad

```bash
python manage.py test core        # 12 pruebas: página, leads, validación, honeypot, rate limit
python -m ruff check .            # linting
python -m ruff format --check .   # formato
DEBUG=False SECRET_KEY=... python manage.py check --deploy --settings=config.settings.prod
```

## Animaciones: qué se usa y por qué

- **GSAP + ScrollTrigger** — motor de scroll: escena fija (pin) de 4 pasos con
  `scrub` y timeline maestro, banda horizontal de servicios con pin + `scrub` +
  `snap`, parallax rural y barra de progreso.
- **GSAP SplitText** — revelado de titulares por línea/palabra/letra e
  iluminación palabra por palabra del manifiesto.
- **Lenis** — scroll suave, sincronizado con ScrollTrigger
  (`lenis.on('scroll', ScrollTrigger.update)` + `gsap.ticker`).
- **Three.js** — red 3D de nodos y líneas de luz en el hero; reacciona al mouse
  y al scroll; se pausa fuera de pantalla (IntersectionObserver) y se degrada a
  canvas 2D en móviles con pocos recursos. Se carga con `import()` diferido.
- **Lottie (lottie-web/light)** — microanimaciones de íconos de servicios y de
  los pasos de la escena fija. Archivos en `static/lottie/` (regenera con
  `npm run lottie`). Si un JSON falta o falla, hay fallback a SVG animado con
  GSAP o al ícono de texto.

**Agregar una animación Lottie:** exporta desde After Effects con Bodymovin,
guarda el JSON en `static/lottie/` y pon su nombre en el campo "Archivo Lottie"
del servicio o paso correspondiente en el admin.

## Accesibilidad y rendimiento

- `prefers-reduced-motion`: se desactivan pin, scrub, Three.js, Lenis y Lottie;
  el contenido se muestra estático y completo (ver `main.css`).
- El HTML es legible sin JS (los revelados solo se ocultan con `html.js`).
- `will-change` solo donde se anima; Three.js y Lottie son carga diferida;
  objetivo 60 fps y Lighthouse Performance ≥ 85 en móvil.

## Despliegue

**Docker Compose (web + PostgreSQL):**

```bash
docker compose up -d --build
```

**Plataformas tipo Heroku/Render:** usa el `Procfile`
(`gunicorn config.wsgi`). Configura las variables de entorno de la tabla anterior
con `DEBUG=False`, `DATABASE_URL` de PostgreSQL y `SECRET_KEY`.

**Producción con Dockerfile multi-stage:** la etapa Node compila el frontend con
esbuild y la etapa Python ejecuta `collectstatic` + gunicorn con WhiteNoise.

## Estructura

```
config/                  Proyecto Django (settings base/dev/prod, urls, wsgi/asgi)
core/                    App: modelos, admin, formulario, vistas, seed_site, tests
frontend/                Fuentes del frontend (js/ módulos ES, css/ con variables)
static/lottie/           Animaciones Lottie (JSON)
static/js|css/dist/      Salida del build de esbuild (generado)
templates/               base.html + parciales por sección + 404/500
```

## Licencia

Uso interno de INTERNETWORK.
