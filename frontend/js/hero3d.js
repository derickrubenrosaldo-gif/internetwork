/* Hero: red 3D de nodos y conexiones con Three.js.
   - requestAnimationFrame controlado, pausa fuera de pantalla
   - reacciona al mouse y al scroll (inclinación de cámara)
   - se degrada a canvas 2D en móviles con pocos recursos
   - carga diferida (dynamic import) para no pagar el peso en todos lados */
const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));

export async function initHero3D(reduced) {
  const canvas = document.getElementById("net");
  if (!canvas || reduced) return; // movimiento reducido: fondo estático

  const weakDevice =
    (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4) ||
    (navigator.connection && navigator.connection.saveData) ||
    (matchMedia("(pointer: coarse)").matches &&
      Math.min(screen.width, screen.height) < 480);

  if (weakDevice) {
    initCanvas2D(canvas);
    return;
  }

  try {
    const THREE = await import("three");
    initThreeScene(canvas, THREE);
  } catch (error) {
    initCanvas2D(canvas); // degradación elegante
  }
}

function initThreeScene(canvas, THREE) {
  const renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
    powerPreference: "low-power",
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
  camera.position.set(0, 0, 14);

  /* Nodos (partículas) */
  const COUNT = 200;
  const positions = new Float32Array(COUNT * 3);
  for (let i = 0; i < COUNT * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 32;
    positions[i + 1] = (Math.random() - 0.5) * 20;
    positions[i + 2] = (Math.random() - 0.5) * 14;
  }
  const nodesGeometry = new THREE.BufferGeometry();
  nodesGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const nodes = new THREE.Points(
    nodesGeometry,
    new THREE.PointsMaterial({
      color: 0x0a7cbe,
      size: 0.09,
      transparent: true,
      opacity: 0.85,
    })
  );
  scene.add(nodes);

  /* Líneas de luz entre nodos cercanos */
  const linePositions = [];
  const pos = nodesGeometry.attributes.position.array;
  const MAX_DIST = 11;
  for (let i = 0; i < COUNT; i++) {
    for (let j = i + 1; j < COUNT; j++) {
      const dx = pos[i * 3] - pos[j * 3];
      const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
      const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
      if (dx * dx + dy * dy + dz * dz < MAX_DIST * MAX_DIST) {
        linePositions.push(
          pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2],
          pos[j * 3], pos[j * 3 + 1], pos[j * 3 + 2]
        );
      }
    }
  }
  const linesGeometry = new THREE.BufferGeometry();
  linesGeometry.setAttribute("position", new THREE.Float32BufferAttribute(linePositions, 3));
  const lines = new THREE.LineSegments(
    linesGeometry,
    new THREE.LineBasicMaterial({
      color: 0x0b63d6,
      transparent: true,
      opacity: 0.3,
    })
  );
  scene.add(lines);

  /* Mouse: parallax de cámara */
  const mouse = { x: 0, y: 0 };
  const smoothed = { x: 0, y: 0 };
  addEventListener(
    "pointermove",
    (event) => {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = (event.clientY / window.innerHeight) * 2 - 1;
    },
    { passive: true }
  );

  /* Pausa cuando el hero no está visible */
  let running = true;
  let rafId = null;
  const observer = new IntersectionObserver((entries) => {
    running = entries[0].isIntersecting;
    if (running) loop();
    else if (rafId) cancelAnimationFrame(rafId);
  });
  observer.observe(canvas);

  const resize = () => {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  addEventListener("resize", resize, { passive: true });
  resize();

  function loop() {
    rafId = requestAnimationFrame(loop);
    if (!running) return;
    smoothed.x += (mouse.x - smoothed.x) * 0.04;
    smoothed.y += (mouse.y - smoothed.y) * 0.04;
    /* Scroll: ligera inclinación de cámara */
    const scrollTilt = clamp(window.scrollY / (window.innerHeight * 2)) * 0.3;
    camera.rotation.y = smoothed.x * 0.25;
    camera.rotation.x = -smoothed.y * 0.15 + scrollTilt;
    nodes.rotation.z += 0.0004;
    lines.rotation.z += 0.0004;
    renderer.render(scene, camera);
  }
  loop();
}

/* Fallback: red en canvas 2D (móviles débiles o si Three.js no carga) */
function initCanvas2D(canvas) {
  const ctx = canvas.getContext("2d");
  const dpr = Math.min(window.devicePixelRatio, 2);
  let points = [];
  let running = true;
  let rafId = null;

  const resize = () => {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    const count = Math.round((width * height) / 15000);
    points = Array.from({ length: count }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.35 * dpr,
      vy: (Math.random() - 0.5) * 0.35 * dpr,
    }));
  };
  resize();
  addEventListener("resize", resize, { passive: true });

  const mouse = { x: -9999, y: -9999 };
  addEventListener(
    "pointermove",
    (event) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = (event.clientX - rect.left) * dpr;
      mouse.y = (event.clientY - rect.top) * dpr;
    },
    { passive: true }
  );

  const LINK = 150 * dpr;

  const observer = new IntersectionObserver((entries) => {
    running = entries[0].isIntersecting;
    if (running) loop();
    else if (rafId) cancelAnimationFrame(rafId);
  });
  observer.observe(canvas);

  function loop() {
    rafId = requestAnimationFrame(loop);
    if (!running) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (const point of points) {
      point.x += point.vx;
      point.y += point.vy;
      if (point.x < 0 || point.x > canvas.width) point.vx *= -1;
      if (point.y < 0 || point.y > canvas.height) point.vy *= -1;
      ctx.fillStyle = "rgba(10,124,190,.85)";
      ctx.beginPath();
      ctx.arc(point.x, point.y, 1.8 * dpr, 0, 7);
      ctx.fill();
    }

    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const a = points[i];
        const b = points[j];
        const dist = Math.hypot(a.x - b.x, a.y - b.y);
        if (dist < LINK) {
          ctx.strokeStyle = `rgba(10,124,190,${(1 - dist / LINK) * 0.35})`;
          ctx.lineWidth = dpr;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
      const m = Math.hypot(points[i].x - mouse.x, points[i].y - mouse.y);
      if (m < LINK * 1.3) {
        ctx.strokeStyle = `rgba(11,99,214,${(1 - m / (LINK * 1.3)) * 0.75})`;
        ctx.beginPath();
        ctx.moveTo(points[i].x, points[i].y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.stroke();
      }
    }
  }
  loop();
}
