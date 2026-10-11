/* Filtro dinámico de cobertura: escribe y solo quedan las localidades que
   coinciden. Evita listar 69 localidades a mano y ahorra espacio. */

export function initCoverageFilter() {
  const input = document.getElementById("coverageFilter");
  const details = document.querySelector(".coverage-all");
  if (!input || !details) return;

  const grid = details.querySelector(".coverage-grid");
  const groups = [...details.querySelectorAll(".coverage-group")];
  const empty = document.getElementById("coverageEmpty");
  const count = document.getElementById("coverageCount");
  const total = groups.reduce((n, g) => n + g.querySelectorAll("li").length, 0);

  const apply = () => {
    const query = input.value.trim().toLowerCase();
    if (query) details.open = true; // al buscar, se despliega el listado
    let matches = 0;

    groups.forEach((group) => {
      const heading = group.querySelector("h3");
      /* Si coincide el municipio, se muestran todas sus localidades. */
      const municipalityMatches = heading.textContent.toLowerCase().includes(query);
      let visible = 0;

      group.querySelectorAll("li").forEach((item) => {
        const hit =
          !query || municipalityMatches || item.textContent.toLowerCase().includes(query);
        item.hidden = !hit;
        if (hit) visible += 1;
      });

      group.hidden = visible === 0;
      matches += visible;
    });

    if (empty) empty.hidden = !query || matches > 0;
    if (count) {
      count.textContent = query
        ? `${matches} de ${total} localidades`
        : `${total} localidades`;
    }
  };

  input.addEventListener("input", apply);
  grid?.addEventListener("submit", (event) => event.preventDefault());
  apply();
}
