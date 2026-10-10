/* Banda horizontal de servicios: pin + scrub + snap suave por tarjeta. */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export function initServicesScroller(reduced) {
  const section = document.querySelector(".hscroll");
  const track = document.getElementById("track");
  if (!section || !track) return;

  if (reduced) {
    /* Sin animación: mostramos el ícono estático en lugar de Lottie */
    section.querySelectorAll(".lottie-icon").forEach((el) => {
      const icon = document.createElement("span");
      icon.textContent = el.dataset.icon || "◈";
      el.replaceWith(icon);
    });
    return; // con movimiento reducido: tarjetas apiladas (ver CSS)
  }

  loadServiceLottie(section);

  const cards = gsap.utils.toArray(".card");
  if (cards.length < 2) return;

  const amount = () =>
    track.scrollWidth - window.innerWidth + window.innerWidth * 0.08;

  gsap.to(track, {
    x: () => -amount(),
    ease: "none",
    scrollTrigger: {
      trigger: ".hscroll",
      start: "top top",
      end: () => `+=${amount()}`,
      scrub: 1,
      pin: true,
      anticipatePin: 1,
      invalidateOnRefresh: true,
      snap: {
        snapTo: 1 / (cards.length - 1),
        duration: { min: 0.2, max: 0.8 },
        ease: "power1.inOut",
      },
    },
  });
}

/* Microanimaciones Lottie de los íconos: carga diferida al acercarse.
   Si fallan, se muestra el ícono de texto (data-icon). */
async function loadServiceLottie(section) {
  const containers = Array.from(section.querySelectorAll(".lottie-icon"));
  if (!containers.length) return;

  let lottie = null;
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach(async (entry) => {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        try {
          lottie = lottie || (await import("lottie-web/build/player/lottie_light.js")).default;
          lottie.loadAnimation({
            container: entry.target,
            path: entry.target.dataset.lottie,
            renderer: "svg",
            loop: true,
            autoplay: true,
          });
        } catch (error) {
          const icon = document.createElement("span");
          icon.textContent = entry.target.dataset.icon || "◈";
          entry.target.replaceWith(icon);
        }
      });
    },
    { rootMargin: "200px" }
  );
  containers.forEach((container) => io.observe(container));
}
