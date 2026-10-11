/* Escena fija (pin) con 4 pasos: timeline maestro con scrub.
   La fijación visual la hace el `position: sticky` del CSS y el scrubbing el
   ScrollTrigger, así funciona igual sin depender del pin de GSAP. */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

let lottieItems = [];

/* Colores del contador de pasos (mismos valores que la paleta CSS) */
const DOT_IDLE = "rgba(11,33,56,.16)";
const DOT_ACTIVE = "#0b63d6";

export function initStory(reduced) {
  const story = document.querySelector(".story");
  if (!story) return;

  const steps = gsap.utils.toArray("#steps .step");
  const items = gsap.utils.toArray("#visuals .visual-item");
  const dots = gsap.utils.toArray("#counter i");
  const bg = document.getElementById("storyBg");
  const glows = (bg?.dataset.glows || "").split("|").filter(Boolean);

  if (!steps.length) return;

  if (reduced) {
    /* Contenido estático: todos los pasos visibles (ver CSS), sin Lottie */
    steps.forEach((step) => {
      step.classList.add("active");
      step.style.opacity = 1;
      step.style.transform = "none";
    });
    dots.forEach((dot) => dot.classList.add("active"));
    return;
  }

  loadStoryLottie(items, steps.length, syncWithProgress);

  const timeline = gsap.timeline({
    defaults: { ease: "power2.inOut" },
    scrollTrigger: {
      trigger: ".story",
      start: "top top",
      end: "bottom bottom",
      scrub: 0.6,
      invalidateOnRefresh: true,
      onUpdate: (self) => syncWithProgress(self.progress),
    },
  });

  /* Estado inicial: primer paso visible */
  timeline
    .set(steps, { opacity: 0, y: 40 })
    .set(steps[0], { opacity: 1, y: 0 })
    .set(items, { opacity: 0, scale: 0.88 })
    .set(items[0], { opacity: 1, scale: 1 })
    .set(dots, { backgroundColor: DOT_IDLE, width: 34 })
    .set(dots[0], { backgroundColor: DOT_ACTIVE, width: 54 });

  if (glows[0] && bg) timeline.set(bg, { "--glow": glows[0] });

  /* Master timeline: un bloque por transición de paso */
  for (let i = 1; i < steps.length; i++) {
    const t = i;
    timeline
      .to(steps[i - 1], { opacity: 0, y: -40, duration: 0.9 }, t)
      .to(steps[i], { opacity: 1, y: 0, duration: 0.9 }, t)
      .to(items[i - 1], { opacity: 0, scale: 0.88, duration: 0.9 }, t)
      .to(items[i], { opacity: 1, scale: 1, duration: 0.9 }, t)
      .to(dots[i - 1], { backgroundColor: DOT_IDLE, width: 34, duration: 0.5 }, t)
      .to(dots[i], { backgroundColor: DOT_ACTIVE, width: 54, duration: 0.5 }, t);
    if (glows[i] && bg) {
      timeline.to(bg, { "--glow": glows[i], duration: 0.9 }, t);
    }
  }
}

/* Sincroniza las animaciones Lottie con el progreso del scrub.
   El frame se limita a `totalFrames - 1`: en el frame final (op) Lottie
   no dibuja nada y el gráfico desaparecería al terminar cada tramo. */
function syncWithProgress(progress) {
  lottieItems.forEach(({ index, anim, total }) => {
    const segStart = index / (total - 1 || 1);
    const segEnd = (index + 1) / (total - 1 || 1);
    const local = Math.min(1, Math.max(0, (progress - segStart) / (segEnd - segStart)));
    const lastFrame = Math.max(0, anim.totalFrames - 1);
    anim.goToAndStop(Math.min(local * anim.totalFrames, lastFrame), true);
  });
}

/* Carga diferida de Lottie para los pasos; fallback: SVG animado con GSAP */
async function loadStoryLottie(items, totalSteps, onProgress) {
  const containers = items.flatMap((item) =>
    Array.from(item.querySelectorAll(".lottie"))
  );
  if (!containers.length) return;

  try {
    const lottie = await import("lottie-web/build/player/lottie_light.js");
    containers.forEach((container) => {
      try {
        const item = container.closest(".visual-item");
        const index = Number(item?.dataset.index || 0);
        const anim = lottie.default.loadAnimation({
          container,
          path: container.dataset.lottie,
          renderer: "svg",
          loop: false,
          autoplay: false,
        });
        lottieItems.push({ index, anim, total: totalSteps });
        container.classList.add("loaded");
        const svg = item?.querySelector("svg");
        if (svg) svg.style.display = "none";
        onProgress(0);
      } catch (error) {
        animateSvgFallback(container.closest(".visual-item"));
      }
    });
  } catch (error) {
    /* lottie-web no disponible: SVGs animados con GSAP */
    items.forEach((item) => animateSvgFallback(item));
  }
}

/* Fallback: efecto de trazo (draw) sobre el SVG del paso */
function animateSvgFallback(item) {
  const svg = item?.querySelector("svg");
  if (!svg) return;
  svg.querySelectorAll("path, circle, rect").forEach((el) => {
    const length = el.getTotalLength?.() || 300;
    el.style.strokeDasharray = length;
    el.style.strokeDashoffset = length;
    gsap.to(el, {
      strokeDashoffset: 0,
      duration: 1.4,
      ease: "power2.out",
      scrollTrigger: { trigger: svg, start: "top 80%", once: true },
    });
  });
}
