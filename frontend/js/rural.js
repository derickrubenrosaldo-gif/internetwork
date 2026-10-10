/* Zonas rurales: parallax de capas con scrub. */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export function initRural(reduced) {
  const rural = document.querySelector(".rural");
  if (!rural || reduced) return; // con movimiento reducido: capas estáticas

  /* Capa de colinas: se mueve más lento que el scroll */
  gsap.to(".hills", {
    y: -90,
    ease: "none",
    scrollTrigger: {
      trigger: ".rural",
      start: "top bottom",
      end: "bottom top",
      scrub: 1,
    },
  });

  /* Parallax diferencial: la colina trasera avanza menos */
  const backHill = rural.querySelector(".hills svg path:first-child");
  if (backHill) {
    gsap.to(backHill, {
      y: 26,
      ease: "none",
      scrollTrigger: {
        trigger: ".rural",
        start: "top bottom",
        end: "bottom top",
        scrub: 1.2,
      },
    });
  }
}
