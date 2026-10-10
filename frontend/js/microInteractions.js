/* Microinteracciones de escritorio: cursor personalizado,
   botones magnéticos y tarjetas con tilt 3D + brillo al cursor. */
import gsap from "gsap";

export function initMicroInteractions(reduced) {
  if (reduced) return;
  if (!matchMedia("(pointer: fine)").matches) return; // solo puntero fino

  initCursor();
  initMagneticButtons();
  initTiltCards();
}

function initCursor() {
  const cursor = document.getElementById("cursor");
  const ring = document.getElementById("cursor-ring");
  if (!cursor || !ring) return;

  document.documentElement.classList.add("cursor-on");

  const xTo = gsap.quickTo(cursor, "x", { duration: 0.12, ease: "power3" });
  const yTo = gsap.quickTo(cursor, "y", { duration: 0.12, ease: "power3" });
  const ringXTo = gsap.quickTo(ring, "x", { duration: 0.45, ease: "power3" });
  const ringYTo = gsap.quickTo(ring, "y", { duration: 0.45, ease: "power3" });

  addEventListener(
    "mousemove",
    (event) => {
      xTo(event.clientX);
      yTo(event.clientY);
      ringXTo(event.clientX);
      ringYTo(event.clientY);
    },
    { passive: true }
  );

  document.querySelectorAll("a, button, .card").forEach((el) => {
    el.addEventListener("mouseenter", () =>
      document.documentElement.classList.add("cursor-hover")
    );
    el.addEventListener("mouseleave", () =>
      document.documentElement.classList.remove("cursor-hover")
    );
  });
}

function initMagneticButtons() {
  document.querySelectorAll(".btn").forEach((button) => {
    const strength = 0.25;
    button.addEventListener("mousemove", (event) => {
      const rect = button.getBoundingClientRect();
      const x = event.clientX - rect.left - rect.width / 2;
      const y = event.clientY - rect.top - rect.height / 2;
      gsap.to(button, { x: x * strength, y: y * strength, duration: 0.4, ease: "power3.out" });
    });
    button.addEventListener("mouseleave", () => {
      gsap.to(button, { x: 0, y: 0, duration: 0.7, ease: "elastic.out(1, 0.4)" });
    });
  });
}

function initTiltCards() {
  document.querySelectorAll("[data-tilt]").forEach((card) => {
    card.addEventListener("mousemove", (event) => {
      const rect = card.getBoundingClientRect();
      const px = (event.clientX - rect.left) / rect.width;
      const py = (event.clientY - rect.top) / rect.height;
      /* Brillo que sigue al cursor (variables CSS) */
      card.style.setProperty("--mx", `${px * 100}%`);
      card.style.setProperty("--my", `${py * 100}%`);
      gsap.to(card, {
        rotateY: (px - 0.5) * 10,
        rotateX: (0.5 - py) * 10,
        transformPerspective: 900,
        duration: 0.5,
        ease: "power2.out",
      });
    });
    card.addEventListener("mouseleave", () => {
      gsap.to(card, { rotateX: 0, rotateY: 0, duration: 0.8, ease: "power3.out" });
    });
  });
}
