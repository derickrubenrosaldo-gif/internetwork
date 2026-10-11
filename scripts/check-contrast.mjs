/* Verifica el contraste WCAG de la paleta del sitio.
   Falla (exit 1) si algún par de texto baja de 4.5:1 (UI/graphics 3:1).

   Uso: npm run a11y:contrast  (se ejecuta también en `npm run build`) */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const css = readFileSync(join(root, "frontend", "css", "main.css"), "utf8");

/* Tokens declarados en :root */
const block = css.match(/:root\s*\{([\s\S]*?)\}/);
if (!block) {
  console.error("No se encontró el bloque :root en frontend/css/main.css");
  process.exit(1);
}
const tokens = {};
for (const line of block[1].split("\n")) {
  const match = line.match(/^\s*(--[a-z0-9-]+):\s*(#[0-9a-fA-F]{3,8})\s*;/);
  if (match) tokens[match[1]] = match[2];
}

function channel(value) {
  const c = value / 255;
  return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

function luminance(hex) {
  const clean = hex.replace("#", "");
  const full =
    clean.length === 3
      ? clean
          .split("")
          .map((c) => c + c)
          .join("")
      : clean.slice(0, 6);
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16));
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

function ratio(a, b) {
  const [l1, l2] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

/* Pares obligatorios: [texto, fondo, mínimo] */
const WHITE = "#ffffff";
const PAIRS = [
  ["--ink", "--bg", 4.5],
  ["--text", "--bg", 4.5],
  ["--muted", "--bg", 4.5],
  ["--muted", "--soft", 4.5],
  ["--text", "--soft", 4.5],
  ["--ink", "--tint", 4.5],
  ["--blue", "--bg", 4.5],
  ["--blue", "--soft", 4.5],
  ["--navy-text", "--navy", 4.5],
  ["--navy-link", "--navy", 4.5],
  ["--success", "--bg", 4.5],
  ["--warn", "--bg", 4.5],
  ["--danger", "--bg", 4.5],
  [WHITE, "--blue", 4.5], // texto blanco sobre botón primario
  ["--border-strong", "--bg", 3.0], // borde de controles (UI)
  ["--sky", "--bg", 3.0], // fin de degradado de titulares grandes
];

let failed = 0;
for (const [fgToken, bgToken, min] of PAIRS) {
  const fg = fgToken.startsWith("#") ? fgToken : tokens[fgToken];
  const bg = bgToken.startsWith("#") ? bgToken : tokens[bgToken];
  if (!fg || !bg) {
    console.error(`✗ Token no definido: ${!fg ? fgToken : bgToken}`);
    failed += 1;
    continue;
  }
  const value = ratio(fg, bg);
  const ok = value >= min;
  if (!ok) failed += 1;
  const label = `${fgToken} sobre ${bgToken}`;
  console.log(
    `${ok ? "✓" : "✗"} ${label.padEnd(34)} ${value.toFixed(2)}:1 (mín ${min}:1)`
  );
}

if (failed) {
  console.error(`\n${failed} par(es) no cumplen el contraste mínimo.`);
  process.exit(1);
}
console.log("\nContraste WCAG correcto en todos los pares.");
