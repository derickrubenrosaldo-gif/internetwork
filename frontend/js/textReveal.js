/* Revelado de texto con GSAP SplitText:
   - titulares por línea/palabra/letra
   - manifiesto iluminado palabra por palabra con scrub */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

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
    color: "#f5f9ff",
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

/* Titulares: SplitText por línea/palabra/letra con fallback simple */
async function revealHeadings() {
  const headings = [
    document.querySelector(".hero h1"),
    ...document.querySelectorAll(".h-head h2, .rural h2, .why h2, .contact h2"),
  ].filter(Boolean);
  if (!headings.length) return;

  try {
    const { SplitText } = await import("gsap/SplitText");
    gsap.registerPlugin(SplitText);

    headings.forEach((heading) => {
      const split = SplitText.create(heading, {
        type: "lines,words,chars",
      });
      if (heading.closest(".hero")) {
        /* Hero: entrada tras el preloader, letra por letra */
        gsap.from(split.chars, {
          yPercent: 110,
          opacity: 0,
          rotateZ: 4,
          duration: 1.1,
          ease: "power4.out",
          stagger: 0.02,
          delay: 1.0,
        });
      } else {
        /* Secciones: revelado por línea al entrar en vista */
        gsap.from(split.lines, {
          yPercent: 60,
          opacity: 0,
          duration: 1,
          ease: "power3.out",
          stagger: 0.08,
          scrollTrigger: { trigger: heading, start: "top 85%", once: true },
        });
      }
    });
  } catch (error) {
    /* Fallback sin SplitText: revelado del titular completo */
    headings.forEach((heading) => {
      const isHero = heading.closest(".hero");
      gsap.from(heading, {
        y: 40,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        ...(isHero ? { delay: 1.0 } : {}),
        ...(isHero
          ? {}
          : { scrollTrigger: { trigger: heading, start: "top 85%", once: true } }),
      });
    });
  }
}
