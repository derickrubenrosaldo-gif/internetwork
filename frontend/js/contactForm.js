/* Formulario de contacto: envío por fetch con respuesta JSON,
   animaciones de éxito/error con GSAP y continuación por WhatsApp. */
import gsap from "gsap";

export function initContactForm() {
  const form = document.getElementById("quoteForm");
  if (!form) return;

  const note = document.getElementById("formNote");
  const actions = document.getElementById("formActions");
  const whatsappBtn = document.getElementById("whatsappBtn");
  const submitBtn = document.getElementById("submitBtn");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    /* Validación nativa + visual */
    if (!form.checkValidity()) {
      markInvalid(form);
      form.reportValidity();
      return;
    }

    setLoading(true);
    clearState();

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: {
          "X-Requested-With": "fetch",
          "X-CSRFToken": getCookie("csrftoken"),
        },
      });
      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        form.reset();
        showSuccess(data);
      } else {
        showError(
          data.message || "No pudimos enviar tu solicitud. Intenta de nuevo."
        );
        if (data.errors) markFieldErrors(form, data.errors);
      }
    } catch (error) {
      showError("Sin conexión. Revisa tu red e intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  });

  function setLoading(loading) {
    submitBtn.disabled = loading;
    submitBtn.textContent = loading ? "Enviando…" : "Enviar solicitud";
  }

  function clearState() {
    note.classList.remove("success", "error");
    actions.hidden = true;
    form.querySelectorAll(".invalid").forEach((el) => el.classList.remove("invalid"));
  }

  function showSuccess(data) {
    note.textContent = data.message || "Solicitud enviada.";
    note.classList.add("success");
    gsap.fromTo(form, { scale: 0.985 }, { scale: 1, duration: 0.5, ease: "back.out(2)" });
    gsap.fromTo(note, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.5 });

    /* Botón "Continuar por WhatsApp" con mensaje prellenado */
    if (data.whatsapp_url) {
      whatsappBtn.href = data.whatsapp_url;
      actions.hidden = false;
      gsap.from(actions, { opacity: 0, y: 10, duration: 0.6, delay: 0.2 });
    }
  }

  function showError(message) {
    note.textContent = message;
    note.classList.add("error");
    form.classList.remove("shake");
    void form.offsetWidth; /* reinicia la animación */
    form.classList.add("shake");
    gsap.fromTo(note, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.4 });
  }

  function markInvalid(formEl) {
    formEl.querySelectorAll("[required]").forEach((field) => {
      const empty = field.type === "checkbox" ? !field.checked : !field.value.trim();
      if (empty) field.classList.add("invalid");
    });
  }

  function markFieldErrors(formEl, errors) {
    Object.keys(errors).forEach((name) => {
      const field = formEl.elements[name];
      field?.classList.add("invalid");
    });
  }

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }
}
