/* Revelado de texto con GSAP SplitText:
   - titulares por línea (el resaltado en degradado conserva su texto intacto:
     si se parte en palabras/letras, `background-clip:text` deja de tener texto
     propio que recortar y el degradado desaparece)
   - hero: la primera parte se anima letra por letra y el resaltado entra aparte
   - manifiesto iluminado palabra por palabra con scrub */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { token } from "./theme.js";

export function initTextReveal(reduced) {
  if (reduced) {
    /* Todo visible y estático */
    document.querySelectorAll(".statement .w").forEach((word) => {
      word.style.color = "";
    });
    return;
  }

  initStatement();
  revealHeadings();
}

/* Manifiesto: cada palabra se ilumina al pasar el scrub */
function initStatement() {
  const statement = document.getElementById("statement");
  if (!statement) return;

  statement.innerHTML = statement.textContent
    .split(" ")
    .map((word) => `<span class="w">${word}</span>`)
    .join(" ");

  const words = statement.querySelectorAll(".w");
  gsap.to(words, {
    color: token("--ink", "#0a2540"), /* lee el token de diseño */
    stagger: 0.08,
    ease: "none",
    scrollTrigger: {
      trigger: ".statement",
      start: "top 75%",
      end: "center 40%",
      scrub: 1,
    },
  });
}

/* Titulares: la entrada del hero (letra a letra) y el resto por líneas */
async function revealHeadings() {
  const heroTitle = document.querySelector(".hero h1 .hero-title");
  const heroGrad = document.querySelector(".hero h1 .hero-grad");
  const headings = [
    ...document.querySelectorAll(
      ".h-head h2, .rural h2, .plans h2, .dedicated h2, .coverage h2, .why h2, .contact h2"
    ),
  ].filter(Boolean);

  if (!heroTitle && !headings.length) return;

  try {
    const { SplitText } = await import("gsap/SplitText");
    gsap.registerPlugin(SplitText);

    /* Hero: primera parte letra por letra, resaltado como bloque */
    if (heroTitle) {
      const split = SplitText.create(heroTitle, { type: "chars" });
      gsap.from(split.chars, {
        yPercent: 110,
        opacity: 0,
        rotateZ: 4,
        duration: 1.1,
        ease: "power4.out",
        stagger: 0.02,
        delay: 1.0,
      });
    }
    if (heroGrad) {
      gsap.from(heroGrad, {
        yPercent: 70,
        opacity: 0,
        duration: 1.1,
        ease: "power4.out",
        delay: 1.15,
      });
    }

    /* Secciones: revelado por línea al entrar en vista */
    headings.forEach((heading) => {
      const split = SplitText.create(heading, { type: "lines" });
      gsap.from(split.lines, {
        yPercent: 60,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        stagger: 0.08,
        scrollTrigger: { trigger: heading, start: "top 85%", once: true },
      });
    });
  } catch (error) {
    /* Fallback sin SplitText: revelado del titular completo */
    const targets = [heroTitle, heroGrad, ...headings].filter(Boolean);
    targets.forEach((el) => {
      const isHero = Boolean(el.closest(".hero"));
      gsap.from(el, {
        y: 40,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        ...(isHero ? { delay: 1.0 } : {}),
        ...(isHero
          ? {}
          : { scrollTrigger: { trigger: el, start: "top 85%", once: true } }),
      });
    });
  }
}
