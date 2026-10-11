/* Formulario de pagos: envío por fetch con respuesta JSON;
   al exitoso muestra la referencia y las instrucciones de pago. */
import gsap from "gsap";

export function initPaymentForm() {
  const form = document.getElementById("payForm");
  if (!form) return;

  const note = document.getElementById("payNote");
  const result = document.getElementById("payResult");
  const refEl = document.getElementById("payRef");
  const instrEl = document.getElementById("payInstructions");
  const submitBtn = document.getElementById("paySubmitBtn");

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
          data.message || "No pudimos registrar tu pago. Intenta de nuevo."
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
    submitBtn.textContent = loading ? "Registrando…" : "Registrar pago";
  }

  function clearState() {
    note.classList.remove("success", "error");
    result.hidden = true;
    form.querySelectorAll(".invalid").forEach((el) => el.classList.remove("invalid"));
  }

  function showSuccess(data) {
    note.textContent = data.message || "Pago registrado.";
    note.classList.add("success");
    gsap.fromTo(form, { scale: 0.985 }, { scale: 1, duration: 0.5, ease: "back.out(2)" });
    gsap.fromTo(note, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.5 });

    if (data.reference) {
      refEl.textContent = data.reference;
      instrEl.textContent = data.instructions || "";
      result.hidden = false;
      gsap.from(result, { opacity: 0, y: 12, duration: 0.6, delay: 0.2 });
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
      if (!field.value.trim()) field.classList.add("invalid");
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
