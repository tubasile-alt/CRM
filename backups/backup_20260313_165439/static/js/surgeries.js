/* =====================================================
   SURGERIES MODULE
   Responsável apenas pelo modal e evolução de cirurgia
   ===================================================== */

(function () {
  "use strict";

  const core = window.ProntuarioCore;

  function parseDateSafe(dateStr) {
    const d = new Date(dateStr);
    if (!isNaN(d.getTime())) return d;

    const parts = String(dateStr).split("/");
    if (parts.length === 3) {
      return new Date(parts[2], parts[1] - 1, parts[0]);
    }

    return new Date();
  }

  function formatDatetimeLocal(date) {
    const pad = (n) => String(n).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  }

  function getSuggestedDate(type, surgeryDate) {
    const d = new Date(surgeryDate);

    if (type === "7_days") d.setDate(d.getDate() + 7);
    if (type === "5_months") d.setMonth(d.getMonth() + 5);
    if (type === "1_year") d.setFullYear(d.getFullYear() + 1);

    return formatDatetimeLocal(d);
  }

  function getChecklist(type) {
    if (type === "7_days") {
      return `
      <div class="border rounded p-3 bg-light mb-3">

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="necrose">
      <label class="form-check-label">Necrose</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="crostas">
      <label class="form-check-label">Crostas</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="falha">
      <label class="form-check-label">Falha</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="desenho_torto">
      <label class="form-check-label">Desenho torto</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="infeccao_secundaria">
      <label class="form-check-label">Infecção secundária</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="foliculite">
      <label class="form-check-label">Foliculite</label>
      </div>

      </div>`;
    }

    if (type === "5_months") {
      return `
      <div class="border rounded p-3 bg-light mb-3">

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="rarefacao">
      <label class="form-check-label">Rarefação</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="falha_localizada">
      <label class="form-check-label">Falha localizada</label>
      </div>

      </div>`;
    }

    if (type === "1_year") {
      return `
      <div class="border rounded p-3 bg-light mb-3">

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="resultado_otimo">
      <label class="form-check-label">Resultado ótimo</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="resultado_bom">
      <label class="form-check-label">Resultado bom</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="resultado_inferior">
      <label class="form-check-label">Resultado inferior ao esperado</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="paciente_satisfeito">
      <label class="form-check-label">Paciente satisfeito</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="paciente_insatisfeito">
      <label class="form-check-label">Paciente insatisfeito</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="falha">
      <label class="form-check-label">Falha</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="retoque">
      <label class="form-check-label">Precisa de retoque</label>
      </div>

      <div class="form-check">
      <input class="form-check-input evolution-check" type="checkbox" value="segunda_cirurgia">
      <label class="form-check-label">Indicação de segunda cirurgia</label>
      </div>

      </div>`;
    }

    return "";
  }

  function createEvolutionForSurgery(surgeryId, surgeryDateRaw) {

    const surgeryDate = parseDateSafe(surgeryDateRaw);

    const modal = document.createElement("div");
    modal.className = "modal fade";
    modal.id = "surgeryEvolutionModal";

    modal.innerHTML = `
    <div class="modal-dialog modal-lg">
    <div class="modal-content">

    <div class="modal-header">
    <h5 class="modal-title">Nova evolução da cirurgia</h5>
    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
    </div>

    <div class="modal-body">

    <div class="mb-3">
    <label class="form-label"><strong>Tipo de retorno</strong></label>
    <select id="returnType" class="form-select">
    <option value="general">Retorno livre</option>
    <option value="7_days">Retorno 7 dias</option>
    <option value="5_months">Retorno 5 meses</option>
    <option value="1_year">Retorno 1 ano</option>
    </select>
    </div>

    <div class="mb-3">
    <label class="form-label"><strong>Data da evolução</strong></label>
    <input type="datetime-local" id="evolutionDate" class="form-control" value="${formatDatetimeLocal(new Date())}">
    </div>

    <div id="checklistContainer"></div>

    <div class="mb-3">
    <label class="form-label"><strong>Observações</strong></label>
    <textarea id="evolutionContent" class="form-control" rows="5"></textarea>
    </div>

    </div>

    <div class="modal-footer">
    <button class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
    <button class="btn btn-primary" id="saveEvolutionBtn">Salvar</button>
    </div>

    </div>
    </div>`;

    document.body.appendChild(modal);

    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();

    const typeSelect = modal.querySelector("#returnType");
    const checklistContainer = modal.querySelector("#checklistContainer");
    const dateInput = modal.querySelector("#evolutionDate");

    function renderChecklist() {
      const type = typeSelect.value;
      checklistContainer.innerHTML = getChecklist(type);

      if (type !== "general") {
        dateInput.value = getSuggestedDate(type, surgeryDate);
      }
    }

    renderChecklist();

    typeSelect.addEventListener("change", renderChecklist);

    modal.querySelector("#saveEvolutionBtn").addEventListener("click", async () => {
      const checked = Array.from(modal.querySelectorAll(".evolution-check:checked"))
        .map((el) => el.value);

      const notes = modal.querySelector("#evolutionContent").value.trim();
      const returnType = typeSelect.value;

      const checkedLabels = Array.from(modal.querySelectorAll(".evolution-check:checked"))
        .map((el) => el.closest(".form-check")?.innerText?.trim())
        .filter(Boolean);

      const contentParts = [];

      contentParts.push(`[TIPO DE RETORNO] ${returnType}`);

      if (checkedLabels.length) {
        contentParts.push("[CHECKLIST]");
        checkedLabels.forEach((label) => contentParts.push(`- ${label}`));
      }

      if (notes) {
        contentParts.push("[OBSERVAÇÕES]");
        contentParts.push(notes);
      }

      const content = contentParts.join("\n").trim();

      if (!content) {
        alert("Preencha pelo menos uma informação na evolução.");
        return;
      }

      const patientId =
        window.ProntuarioCore?.getPatientId?.() ||
        window.__PRONTUARIO_CONFIG?.patientId;

      if (!patientId) {
        alert("Patient ID não encontrado.");
        return;
      }

      const payload = {
        evolution_date: dateInput.value,
        content: content,
        notes: notes,
        return_type: returnType,
        checked_items: checked
      };

      try {
        await (window.ProntuarioCore?.fetchJson
          ? window.ProntuarioCore.fetchJson(`/api/patient/${patientId}/surgery/${surgeryId}/evolution`, {
              method: "POST",
              body: JSON.stringify(payload)
            })
          : fetch(`/api/patient/${patientId}/surgery/${surgeryId}/evolution`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
              credentials: "same-origin"
            }).then(async (r) => {
              const t = await r.text();
              let d = null;
              try { d = t ? JSON.parse(t) : null; } catch (_) {}
              if (!r.ok) throw new Error((d && (d.error || d.message)) || t || `HTTP ${r.status}`);
              return d;
            }));

        bsModal.hide();

        if (typeof window.loadTimeline === "function") {
          window.loadTimeline();
        }

        if (window.ProntuarioCore?.showAppAlert) {
          window.ProntuarioCore.showAppAlert("Evolução salva com sucesso!", "success");
        } else {
          alert("Evolução salva com sucesso!");
        }
      } catch (err) {
        console.error(err);
        alert(`Erro ao salvar evolução: ${err.message}`);
      }
    });

    modal.addEventListener("hidden.bs.modal", () => {
      modal.remove();
    });

  }

  async function saveSurgery() {
    const pId =
      window.patientId ||
      document.getElementById("detailPatientId")?.value ||
      window.__PRONTUARIO_CONFIG?.patientId;

    if (!pId) {
      if (typeof showAlert === "function") {
        showAlert("Erro: ID do paciente não encontrado.", "danger");
      } else {
        alert("Erro: ID do paciente não encontrado.");
      }
      return;
    }

    const surgeryDate = document.getElementById("surgeryDate")?.value || "";
    const surgicalData = document.getElementById("surgicalData")?.value?.trim() || "";
    const observations = document.getElementById("surgeryObservations")?.value?.trim() || "";

    const surgeryTypes = [];
    [
      "surgeryTypeCapilar",
      "surgeryTypeBodyHair",
      "surgeryTypeSobrancelhas",
      "surgeryTypeBarba",
      "surgeryTypeRetoque"
    ].forEach((id) => {
      const cb = document.getElementById(id);
      if (cb?.checked) surgeryTypes.push(cb.value);
    });

    const surgeryType = surgeryTypes.join(", ");

    if (!surgeryDate) {
      showAlert?.("Selecione a data da cirurgia!", "warning");
      return;
    }

    if (!surgicalData) {
      showAlert?.("Preencha os dados cirúrgicos!", "warning");
      return;
    }

    try {
      const response = await fetch(`/api/patient/${pId}/surgery`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": typeof getCSRFToken === "function" ? getCSRFToken() : ""
        },
        body: JSON.stringify({
          surgery_date: surgeryDate,
          surgical_data: surgicalData,
          observations,
          surgery_type: surgeryType
        })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      showAlert?.("Cirurgia registrada com sucesso!", "success");

      ["surgeryDate", "surgicalData", "surgeryObservations"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.value = "";
      });

      [
        "surgeryTypeCapilar",
        "surgeryTypeBodyHair",
        "surgeryTypeSobrancelhas",
        "surgeryTypeBarba",
        "surgeryTypeRetoque"
      ].forEach((id) => {
        const cb = document.getElementById(id);
        if (cb) cb.checked = false;
      });

      if (typeof window.loadSurgeries === "function") {
        window.loadSurgeries();
      }
    } catch (error) {
      console.error("Erro ao salvar cirurgia:", error);
      showAlert?.(`Erro ao salvar cirurgia: ${error.message}`, "danger");
    }
  }

  window.saveSurgery = saveSurgery;
  window.createEvolutionForSurgery = createEvolutionForSurgery;

})();