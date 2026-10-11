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

  // Anclas del menú con scroll suave. Se aceptan tanto `#seccion` como
  // `/#seccion` (la forma portátil que funciona también fuera del home).
  document.querySelectorAll('a[href*="#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const href = link.getAttribute("href") || "";
      const [path, hash] = href.split("#");
      if (!hash) return;
      // Solo se intercepta si apunta a la página actual.
      if (path && path !== window.location.pathname) return;
      const target = document.getElementById(hash);
      if (!target) return;
      event.preventDefault();
      lenis.scrollTo(target, { offset: -56, duration: 1.2 });
      history.replaceState(null, "", `#${hash}`);
    });
  });

  return lenis;
}
