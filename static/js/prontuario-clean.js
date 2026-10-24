// Prontuário (layout clean): só apresentação. Os dados e as ações continuam em prontuario.js.
(function () {
  // Tags marcadas aparecem como chips na linha do paciente; a edição continua no editor de tags.
  function renderTagChips() {
    const target = document.getElementById("patientTagChips");
    if (!target) return;
    target.innerHTML = "";
    document.querySelectorAll(".tag-checkbox:checked").forEach((input) => {
      const chip = document.createElement("span");
      chip.className = "pr-tag-chip";
      chip.style.setProperty("--tag-color", input.dataset.tagColor || "#0050a0");
      chip.textContent = input.dataset.tagName || "";
      target.appendChild(chip);
    });
  }

  // Resumo IA: uma linha, com "Ver mais" para ler o texto completo e o status.
  function setupAISummaryToggle() {
    const card = document.getElementById("prontuarioAISummaryCard");
    const toggle = document.getElementById("aiSummaryToggle");
    if (!card || !toggle) return;
    toggle.addEventListener("click", () => {
      const open = !card.classList.contains("is-open");
      card.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "Ver menos" : "Ver mais";
    });
  }

  function init() {
    renderTagChips();
    document.querySelectorAll(".tag-checkbox").forEach((input) => input.addEventListener("change", renderTagChips));
    setupAISummaryToggle();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
