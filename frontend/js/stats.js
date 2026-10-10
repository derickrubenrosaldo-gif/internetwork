/* Banda de resultados: contadores animados al entrar en vista.
   Interpreta "+500", "99.9%", "24/7" (prefijo + número + sufijo). */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export function initStats(reduced) {
  const stats = document.querySelectorAll(".stat b");
  if (!stats.length) return;

  if (reduced) return; // contenido estático: las cifras ya están en el HTML

  stats.forEach((el) => {
    const raw = el.textContent.trim();
    const match = raw.match(/^([^\d]*)(\d[\d.,]*)([\s\S]*)$/);
    if (!match) return;

    const [, prefix = "", number = "0", suffix = ""] = match;
    const target = parseFloat(number.replace(/,/g, ""));
    const decimals = number.includes(".") ? Math.max(number.split(".")[1].length, 1) : 0;
    const state = { value: 0 };

    gsap.to(state, {
      value: target,
      duration: 2,
      ease: "power2.out",
      scrollTrigger: { trigger: el, start: "top 88%", once: true },
      onUpdate: () => {
        el.textContent = `${prefix}${state.value.toFixed(decimals)}${suffix}`;
      },
    });
  });
}
