/* Puente entre el CSS y el JS: el JS nunca hardcodea colores.
   Lee los tokens de diseño definidos en :root (única fuente de verdad). */

export function token(name, fallback = "") {
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return value || fallback;
}

/* Convierte un token de color a [r, g, b] normalizados (0-1). */
export function tokenRgb(name, fallback = [0, 0, 0]) {
  const raw = token(name);
  if (!raw) return fallback;
  const hex = raw.replace("#", "");
  if (/^[0-9a-f]{3}$/i.test(hex)) {
    return hex.split("").map((c) => parseInt(c + c, 16) / 255);
  }
  if (/^[0-9a-f]{6}$/i.test(hex)) {
    return [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  }
  const match = raw.match(/rgba?\(([^)]+)\)/);
  if (match) {
    return match[1]
      .split(",")
      .slice(0, 3)
      .map((value) => parseFloat(value) / 255);
  }
  return fallback;
}

/* Token de color como número 0xRRGGBB (Three.js). */
export function tokenHex(name, fallback = 0x000000) {
  const [r, g, b] = tokenRgb(name);
  return (Math.round(r * 255) << 16) | (Math.round(g * 255) << 8) | Math.round(b * 255);
}

/* Token de color como cadena rgba() con alfa (canvas 2D). */
export function tokenRgba(name, alpha = 1, fallback = [0, 0, 0]) {
  const [r, g, b] = tokenRgb(name, fallback);
  return `rgba(${Math.round(r * 255)},${Math.round(g * 255)},${Math.round(b * 255)},${alpha})`;
}
