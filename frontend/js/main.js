/* Orquestador del frontend INTERNETWORK.
   Carga cada módulo de forma aislada: si uno falla, el resto sigue. */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { initSmoothScroll } from "./smoothScroll.js";
import { initTextReveal } from "./textReveal.js";
import { initStory } from "./story.js";
import { initServicesScroller } from "./servicesScroller.js";
import { initRural } from "./rural.js";
import { initMicroInteractions } from "./microInteractions.js";
import { initContactForm } from "./contactForm.js";
import { initPaymentForm } from "./paymentForm.js";
import { initHero3D } from "./hero3d.js";
import { initStats } from "./stats.js";
import { initNav } from "./nav.js";

gsap.registerPlugin(ScrollTrigger);

const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
document.documentElement.classList.add("js");

/* Preloader: lo oculta GSAP; si algo falla, un temporizador de seguridad
   (y la animación CSS) garantizan que desaparece. */
const preloader = document.getElementById("preloader");
if (preloader) {
  if (REDUCED) {
    preloader.remove();
  } else {
    gsap.to(preloader, {
      autoAlpha: 0,
      duration: 0.6,
      delay: 0.9,
      ease: "power2.out",
      onComplete: () => preloader.remove(),
    });
    setTimeout(() => {
      preloader.style.opacity = "0";
      preloader.style.visibility = "hidden";
    }, 1800);
  }
}

/* Barra de progreso del scroll (GSAP ScrollTrigger; oculta con movimiento reducido) */
const progress = document.getElementById("progress");
if (progress && !REDUCED) {
  gsap.to(progress, {
    scaleX: 1,
    transformOrigin: "left center",
    ease: "none",
    scrollTrigger: { start: 0, end: "max", scrub: 0.3 },
  });
}

/* Header más sólido al hacer scroll */
const header = document.querySelector("header");
if (header) {
  ScrollTrigger.create({
    start: 40,
    end: "max",
    toggleClass: { targets: header, className: "scrolled" },
  });
}

/* Módulos */
initNav();
const lenis = initSmoothScroll(REDUCED);
initTextReveal(REDUCED);
initStory(REDUCED);
initServicesScroller(REDUCED);
initRural(REDUCED);
initMicroInteractions(REDUCED);
initContactForm();
initPaymentForm();
initHero3D(REDUCED);
initStats(REDUCED);

/* Revelado al hacer scroll: los bloques con .reveal aparecen con .in */
const revealTargets = document.querySelectorAll(".reveal");
if (REDUCED) {
  revealTargets.forEach((el) => el.classList.add("in"));
} else {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("in");
        revealObserver.unobserve(entry.target);
      });
    },
    /* threshold 0: basta con que asome un píxel. Con umbrales mayores, los
       bloques más altos que el viewport (o pegados al final de la página)
       nunca alcanzaban el porcentaje y quedaban invisibles. */
    { threshold: 0, rootMargin: "0px 0px -10% 0px" }
  );
  revealTargets.forEach((el) => revealObserver.observe(el));

  /* Red de seguridad: pase lo que pase, nada queda oculto. */
  const revealFailsafe = () => {
    document
      .querySelectorAll(".reveal:not(.in)")
      .forEach((el) => el.classList.add("in"));
  };
  window.addEventListener("load", () => setTimeout(revealFailsafe, 2500));
  setTimeout(revealFailsafe, 6000);
}

/* Eyebrows: entrada sutil con desplazamiento (los que ya usan .reveal
   se animan con el observador de arriba para no duplicar animaciones) */
if (!REDUCED) {
  gsap.utils
    .toArray(".eyebrow:not(.reveal):not(.step .eyebrow)")
    .forEach((el) => {
      gsap.from(el, {
        x: -16,
        opacity: 0,
        duration: 0.7,
        ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 90%", once: true },
      });
    });
}

/* Nav: resalta la sección visible */
const navLinks = Array.from(document.querySelectorAll("header nav a"));
const sectionIds = ["inicio", "historia", "servicios", "planes", "rural", "nosotros"];
if (navLinks.length) {
  const navObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((link) => {
          link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`);
        });
      });
    },
    { rootMargin: "-40% 0px -55% 0px" }
  );
  sectionIds.forEach((id) => {
    const section = document.getElementById(id);
    if (section) navObserver.observe(section);
  });
}

/* Volver arriba */
const toTop = document.getElementById("toTop");
if (toTop) {
  ScrollTrigger.create({
    start: 600,
    onEnter: () => toTop.classList.add("show"),
    onLeaveBack: () => toTop.classList.remove("show"),
  });
  toTop.addEventListener("click", () => {
    if (lenis) lenis.scrollTo(0, { duration: 1.4 });
    else window.scrollTo({ top: 0, behavior: "smooth" });
  });
}
