/* Scroll suave con Lenis, integrado con GSAP ScrollTrigger. */
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export function initSmoothScroll(reduced) {
  if (reduced) return null; // con movimiento reducido: scroll nativo

  gsap.registerPlugin(ScrollTrigger);

  const lenis = new Lenis({ duration: 1.15, smoothWheel: true });

  // Sincronización oficial Lenis <-> ScrollTrigger
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add((time) => {
    lenis.raf(time * 1000);
  });
  gsap.ticker.lagSmoothing(0);

  // Anclas del menú con scroll suave
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const id = link.getAttribute("href");
      if (!id || id === "#") return;
      const target = document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      lenis.scrollTo(target, { offset: -56, duration: 1.2 });
    });
  });

  return lenis;
}
