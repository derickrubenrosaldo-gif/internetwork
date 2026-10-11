/* Menú principal: hamburguesa accesible y desplegable de "Área de clientes".
   - aria-expanded en el botón, Esc cierra, foco contenido en el menú abierto
   - sin JS el menú de escritorio sigue visible (solo se oculta en móvil por CSS) */

export function initNav() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  const drop = document.querySelector(".nav-drop");
  const dropToggle = document.querySelector(".nav-drop-toggle");
  const dropMenu = document.getElementById("nav-drop-menu");

  if (toggle && nav) {
    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      nav.dataset.open = String(open);
      toggle.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
      if (!open) closeDrop();
    };

    toggle.addEventListener("click", () => {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    nav.addEventListener("click", (event) => {
      if (event.target.closest("a")) setOpen(false);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        if (drop?.classList.contains("is-open")) closeDrop();
        else if (toggle.getAttribute("aria-expanded") === "true") {
          setOpen(false);
          toggle.focus();
        }
      }
      // Foco contenido dentro del menú abierto en móvil.
      if (event.key === "Tab" && nav.dataset.open === "true") {
        const focusables = nav.querySelectorAll("a, button");
        if (!focusables.length) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });

    document.addEventListener("click", (event) => {
      if (
        nav.dataset.open === "true" &&
        !event.target.closest(".site-nav") &&
        !event.target.closest(".nav-toggle")
      ) {
        setOpen(false);
      }
    });
  }

  function closeDrop() {
    if (!dropToggle || !dropMenu) return;
    dropToggle.setAttribute("aria-expanded", "false");
    dropMenu.hidden = true;
    drop?.classList.remove("is-open");
  }

  if (dropToggle && dropMenu) {
    dropToggle.addEventListener("click", () => {
      const open = dropToggle.getAttribute("aria-expanded") === "true";
      dropToggle.setAttribute("aria-expanded", String(!open));
      dropMenu.hidden = open;
      drop.classList.toggle("is-open", !open);
    });

    document.addEventListener("click", (event) => {
      if (drop.classList.contains("is-open") && !event.target.closest(".nav-drop")) {
        closeDrop();
      }
    });
  }
}
