/* Genera las animaciones Lottie (JSON) en static/lottie/.
   Uso: npm run lottie */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const outDir = join(root, "static", "lottie");
mkdirSync(outDir, { recursive: true });

const CYAN = [0.153, 0.769, 1];
const BLUE = [0.031, 0.486, 0.941];

/* ---------- utilidades de formato Lottie ---------- */
const EASE_3 = { i: { x: [0.667, 0.667, 0.667], y: [1, 1, 1] }, o: { x: [0.333, 0.333, 0.333], y: [0, 0, 0] } };
const EASE_1 = { i: { x: [0.667], y: [1] }, o: { x: [0.333], y: [0] } };

const animated = (keys, dims = 1) => ({
  a: 1,
  k: keys.map(([t, v]) => ({ ...(dims === 1 ? EASE_1 : EASE_3), t, s: v })),
});

const fixed = (value) => ({ a: 0, k: value });

const group = (items, name = "grupo") => ({ ty: "gr", it: items, nm: name, np: 3, bm: 0, ix: 1 });

const ellipse = (name, size, position = [0, 0]) => ({
  d: 1, ty: "el", s: fixed(size), p: fixed(position), nm: name, ix: 1,
});

const rect = (name, size, position = [0, 0], radius = 6) => ({
  d: 1, ty: "rc", s: fixed(size), p: fixed(position), r: fixed(radius), nm: name, ix: 1,
});

const path = (name, vertices, closed = true) => ({
  d: 1, ty: "sh",
  ks: fixed({
    i: vertices.map(([x, y]) => [x, y]),
    o: vertices.map(([x, y]) => [x, y]),
    v: vertices,
    c: closed,
  }),
  nm: name, ix: 1,
});

const stroke = (color = CYAN, width = 5, opacity = 100) => ({
  ty: "st", c: fixed(color), o: fixed([opacity]), w: fixed(width), lc: 2, lj: 2, bm: 0, nm: "trazo", ix: 1,
});

const fill = (color = CYAN, opacity = 100) => ({
  ty: "fl", c: fixed(color), o: fixed([opacity]), r: 1, bm: 0, nm: "relleno", ix: 1,
});

const transform = (props = {}) => ({
  a: fixed([0, 0]), p: fixed([0, 0]), s: fixed([100, 100]), r: fixed(0),
  o: fixed(100), sk: fixed(0), sa: fixed(0), ...props, nm: "transform", np: 3,
});

function layer(shapes, { w, h, frames }) {
  return {
    ddd: 0, ind: 1, ty: 4, nm: "capa", sr: 1,
    ks: {
      o: fixed([100]), r: fixed(0), p: fixed([w / 2, h / 2, 0]),
      a: fixed([0, 0, 0]), s: fixed([100, 100, 100]),
    },
    ao: 0, shapes, ip: 0, op: frames, st: 0, bm: 0,
  };
}

function lottie({ w, h, frames, shapes, fps = 30, name = "animacion" }) {
  return {
    v: "5.7.6", fr: fps, ip: 0, op: frames, w, h, nm: name, ddd: 0,
    assets: [], layers: [layer(shapes, { w, h, frames })],
  };
}

/* ---------- animaciones ---------- */

/* 1 · Señal: anillos concéntricos pulsantes */
function signal(size) {
  const s = size / 120;
  const rings = [0, 1, 2].map((i) => {
    const base = (150 - i * 40) * s;
    return group(
      [
        ellipse(`anillo${i}`, [base, base]),
        stroke(CYAN, 5 * s),
        transform({
          o: animated([[0, [55 - i * 12]], [30, [95 - i * 12]], [60, [55 - i * 12]]]),
          s: animated(
            [[0, [92 - i * 6, 92 - i * 6]], [30, [118 - i * 6, 118 - i * 6]], [60, [92 - i * 6, 92 - i * 6]]],
            3
          ),
        }),
      ],
      `anillo-${i}`
    );
  });
  const core = group(
    [ellipse("nucleo", [26 * s, 26 * s]), fill(BLUE), transform({
      s: animated([[0, [100, 100]], [30, [125, 125]], [60, [100, 100]]], 3),
    })],
    "nucleo"
  );
  return lottie({ w: size, h: size, frames: 60, shapes: [...rings, core], name: "senal" });
}

/* 2 · Panel: barras que crecen */
function dashboard(size) {
  const s = size / 120;
  const bars = [0, 1, 2, 3].map((i) => {
    const h = (34 + i * 16) * s;
    const x = (-45 + i * 30) * s;
    return group(
      [
        rect(`barra${i}`, [16 * s, h], [0, h / 2], 5 * s),
        fill(i % 2 ? CYAN : BLUE),
        transform({
          p: animated([[0, [x * 0.4, 40 * s]], [24, [x, 0]], [48, [x, 0]], [60, [x, 0]]], 3),
          s: animated([[0, [100, 100]], [30, [100, 135 + i * 8]], [60, [100, 100]]], 3),
        }),
      ],
      `barra-${i}`
    );
  });
  const line = group(
    [
      path("tendencia", [[-48 * s, 22 * s], [-16 * s, 4 * s], [16 * s, 12 * s], [48 * s, -18 * s]], false),
      stroke(CYAN, 4 * s),
      transform({ o: animated([[0, [0]], [20, [100]]]) }),
    ],
    "tendencia"
  );
  return lottie({ w: size, h: size, frames: 60, shapes: [...bars, line], name: "panel" });
}

/* 3 · Montaña: picos con ondas de señal */
function mountain(size) {
  const s = size / 120;
  const hills = [
    group(
      [
        path("montana-lejana", [[-60 * s, 30 * s], [-20 * s, -28 * s], [20 * s, 30 * s]], false),
        stroke(BLUE, 4 * s, 70),
      ],
      "montana-lejana"
    ),
    group(
      [
        path("montana-cercana", [[-30 * s, 42 * s], [12 * s, -14 * s], [54 * s, 42 * s]], false),
        stroke(CYAN, 5 * s),
      ],
      "montana-cercana"
    ),
  ];
  const waves = [0, 1].map((i) => {
    const r = (26 + i * 18) * s;
    return group(
      [
        path(`onda${i}`, [[-r, 0], [-r * 0.7, -r * 0.7], [0, -r], [r * 0.7, -r * 0.7], [r, 0]], false),
        stroke(CYAN, 4 * s),
        transform({
          o: animated([[0, [30 - i * 10]], [30, [90 - i * 10]], [60, [30 - i * 10]]]),
          p: animated([[0, [0, 34 * s]], [30, [0, 30 * s]], [60, [0, 34 * s]]], 3),
        }),
      ],
      `onda-${i}`
    );
  });
  const base = group(
    [path("base", [[-56 * s, 44 * s], [56 * s, 44 * s]], false), stroke(CYAN, 3 * s, 60)],
    "base"
  );
  return lottie({ w: size, h: size, frames: 60, shapes: [...hills, ...waves, base], name: "montana" });
}

/* 4 · Código: llaves </> con cursor parpadeante */
function code(size) {
  const s = size / 120;
  const bracket = (sign) => {
    const d = sign < 0 ? -1 : 1;
    return group(
      [
        path(
          `llave-${sign}`,
          [
            [d * 18 * s, -30 * s],
            [d * 42 * s, -12 * s],
            [d * 18 * s, 6 * s],
            [d * 42 * s, 24 * s],
            [d * 18 * s, 42 * s],
          ],
          false
        ),
        stroke(CYAN, 6 * s),
      ],
      `llave-${sign}`
    );
  };
  const slash = group(
    [
      path("diagonal", [[10 * s, -34 * s], [-10 * s, 34 * s]], false),
      stroke(BLUE, 6 * s),
      transform({ o: animated([[0, [100]], [40, [100]], [46, [20]], [52, [100]], [60, [100]]]) }),
    ],
    "diagonal"
  );
  return lottie({
    w: size,
    h: size,
    frames: 60,
    shapes: [bracket(-1), bracket(1), slash],
    name: "codigo",
  });
}

/* ---------- escritura de archivos ---------- */
const files = {
  "signal.json": signal(120),
  "dashboard.json": dashboard(120),
  "mountain.json": mountain(120),
  "code.json": code(120),
  "step1-signal.json": signal(240),
  "step2-dashboard.json": dashboard(240),
  "step3-mountain.json": mountain(240),
  "step4-code.json": code(240),
};

for (const [name, data] of Object.entries(files)) {
  writeFileSync(join(outDir, name), `${JSON.stringify(data, null, 2)}\n`);
  console.log(`✓ static/lottie/${name}`);
}
console.log(`${Object.keys(files).length} animaciones Lottie generadas.`);
