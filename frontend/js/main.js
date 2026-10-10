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
import { initHero3D } from "./hero3d.js";
import { initStats } from "./stats.js";

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

/* Barra de progreso del scroll */
const progress = document.getElementById("progress");
if (progress) {
  if (!REDUCED) {
    gsap.to(progress, {
      scaleX: 1,
      transformOrigin: "left center",
      ease: "none",
      scrollTrigger: { start: 0, end: "max", scrub: 0.3 },
    });
  } else {
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = `${max > 0 ? (window.scrollY / max) * 100 : 0}%`;
    };
    addEventListener("scroll", update, { passive: true });
    update();
  }
}

/* Header más sólido al hacer scroll */
const header = document.querySelector("header");
const onScrollNav = () => header?.classList.toggle("scrolled", window.scrollY > 40);
addEventListener("scroll", onScrollNav, { passive: true });
onScrollNav();

/* Módulos */
const lenis = initSmoothScroll(REDUCED);
initTextReveal(REDUCED);
initStory(REDUCED);
initServicesScroller(REDUCED);
initRural(REDUCED);
initMicroInteractions(REDUCED);
initContactForm();
initHero3D(REDUCED);
initStats(REDUCED);

/* Eyebrows: entrada sutil con desplazamiento (excepto en la escena fija) */
if (!REDUCED) {
  gsap.utils.toArray(".eyebrow:not(.step .eyebrow)").forEach((el) => {
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
const sectionIds = ["inicio", "historia", "servicios", "rural", "nosotros"];
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
