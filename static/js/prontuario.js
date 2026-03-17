console.log("prontuario.js carregado v=20260311-right-panel-stable");

let timerInterval = null;
let timerStartTime = null;
let recognition = null;
let activeTextarea = null;

let currentCategory = "patologia";
let cosmeticPlans = [];
let planExecutionsByPlanId = {};
let groupedCosmeticPlans = [];
let editingCosmeticProcedureIndex = null;
let expandedCosmeticPlans = new Set();
let pendingByDateMap = {};
let realizedByDateMap = {};
let selectedNorwood = null;
let activeCosmeticContext = null;
let currentRightPanelMode = null;
let currentHistoricalConsultation = null;

const core = window.ProntuarioCore;

function cfg() {
  return window.__PRONTUARIO_CONFIG || {};
}

function getPatientId() {
  return cfg().patientId || window.patientId || window.__patientId || null;
}

function getAppointmentId() {
  return window.appointmentId ?? cfg().appointmentId ?? null;
}

function getCSRFToken() {
  return (
    document.querySelector('meta[name="csrf-token"]')?.content ||
    cfg().csrfToken ||
    ""
  );
}


function showAlert(message, type = "success") {
  const alertPlaceholder = document.getElementById("alertPlaceholder");
  if (!alertPlaceholder) {
    alert(message);
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show shadow-sm" role="alert">
      <div>${message}</div>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
  alertPlaceholder.append(wrapper);

  setTimeout(() => {
    const alertEl = wrapper.firstElementChild;
    if (!alertEl) return;
    const instance = bootstrap.Alert.getOrCreateInstance(alertEl);
    instance.close();
  }, 5000);
}

/* =========================
   UTIL
========================= */

function nl2br(text) {
  return String(text || "").replace(/\n/g, "<br>");
}


function formatMoneyBRL(value) {
  const n = parseFloat(value || 0);
  return n.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function formatDateBR(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString("pt-BR");
}

function normalizeString(value) {
  return String(value || "").trim();
}

function hasValue(value) {
  return value !== null && value !== undefined && String(value).trim() !== "";
}

function canEditClinical() {
  const v = cfg().canEditClinical;
  return v === true || v === 'true';
}

function ensureClinicalEditAllowed() {
  if (canEditClinical()) return true;
  showAlert('Perfil com acesso somente leitura para conteúdo clínico.', 'warning');
  return false;
}

/* =========================
   DITADO
========================= */

function initSpeechRecognition() {
  if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
    recognition = null;
    return;
  }

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  recognition = new SpeechRecognition();
  recognition.lang = "pt-BR";
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = function (event) {
    let finalTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += `${transcript} `;
      }
    }

    if (activeTextarea && finalTranscript) {
      activeTextarea.value += finalTranscript;
      activeTextarea.dispatchEvent(new Event("input"));
    }
  };

  recognition.onerror = function (event) {
    console.error("Erro no reconhecimento de voz:", event.error);
    stopDictation();
    showAlert(
      "Erro no reconhecimento de voz. Verifique se o microfone está habilitado.",
      "danger"
    );
  };

  recognition.onend = function () {
    const activeButtons = document.querySelectorAll(".dictation-active");
    if (activeButtons.length > 0) {
      stopDictation(false);
    }
  };
}

function startDictation(textareaId, evt = null) {
  if (!recognition) {
    showAlert("Reconhecimento de voz não suportado neste navegador.", "warning");
    return;
  }

  activeTextarea = document.getElementById(textareaId);
  if (!activeTextarea) {
    showAlert("Campo de texto não encontrado.", "danger");
    return;
  }

  const button = evt?.target?.closest("button");
  if (!button) {
    showAlert("Botão de ditado não encontrado.", "warning");
    return;
  }

  if (button.classList.contains("dictation-active")) {
    stopDictation();
    return;
  }

  try {
    document.querySelectorAll(".dictation-active").forEach((btn) => {
      btn.classList.remove("dictation-active");
      btn.innerHTML = '<i class="bi bi-mic"></i> Ditado';
    });

    recognition.start();
    button.classList.add("dictation-active");
    button.innerHTML = '<i class="bi bi-mic-fill"></i> Gravando...';
  } catch (error) {
    console.error("Erro ao iniciar ditado:", error);
    showAlert("Erro ao iniciar ditado.", "danger");
  }
}

function stopDictation(callStop = true) {
  if (recognition && callStop) {
    try {
      recognition.stop();
    } catch (e) {
      console.warn("Falha ao parar reconhecimento:", e);
    }
  }

  document.querySelectorAll(".dictation-active").forEach((button) => {
    button.classList.remove("dictation-active");
    button.innerHTML = '<i class="bi bi-mic"></i> Ditado';
  });

  activeTextarea = null;
}

/* =========================
   TIMER / ATENDIMENTO
========================= */

function updateTimer() {
  if (!timerStartTime) return;

  const elapsed = Math.floor((Date.now() - timerStartTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;

  const display = document.getElementById("timerDisplay");
  if (display) {
    display.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }
}

function startConsultation() {
  const button = document.getElementById("startTimer");
  const display = document.getElementById("timerDisplay");

  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;

    if (button) {
      button.innerHTML = '<i class="bi bi-play-circle"></i> Iniciar Atendimento';
      button.classList.remove("btn-danger");
      button.classList.add("btn-success");
    }

    if (display) {
      display.classList.remove("timer-running");
    }

    return;
  }

  timerStartTime = Date.now();

  if (button) {
    button.innerHTML = '<i class="bi bi-stop-circle"></i> Parar Atendimento';
    button.classList.remove("btn-success");
    button.classList.add("btn-danger");
  }

  if (display) {
    display.classList.add("timer-running");
  }

  timerInterval = setInterval(updateTimer, 1000);
  updateTimer();
}

function getConsultationDuration() {
  if (!timerStartTime) return 0;
  return Math.floor((Date.now() - timerStartTime) / 60000);
}

/* =========================
   PACIENTE / CADASTRO
========================= */

async function updatePatientStars(stars) {
  const patientId = getPatientId();
  if (!patientId) return;

  try {
    const data = await core.fetchJson(`/api/patients/${patientId}/ivp`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({
        ivp_stars: stars,
        ivp_manual_override: true
      })
    });

    if (data.success) {
      showAlert("Classificação atualizada!", "success");
      const container = document.getElementById("patientStarsContainer");
      if (container) {
        container.innerHTML = stars
          ? `<span class="text-warning">${"⭐".repeat(stars)}</span>`
          : "";
      }
    } else {
      showAlert(data.error || "Erro ao atualizar classificação", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao atualizar classificação", "danger");
  }
}

function openAttentionModal() {
  const source = document.getElementById("attentionContent");
  const target = document.getElementById("attentionText");
  if (source && target) {
    target.value = source.textContent || "";
  }
  new bootstrap.Modal(document.getElementById("attentionModal")).show();
}

async function saveAttentionNote() {
  const patientId = getPatientId();
  const content = document.getElementById("attentionText")?.value || "";

  try {
    const result = await core.fetchJson(`/api/patient/${patientId}/attention-note`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({ attention_note: content })
    });

    if (result.success) {
      const attentionContent = document.getElementById("attentionContent");
      const attentionBadge = document.getElementById("attentionBadge");
      if (attentionContent) attentionContent.textContent = content;
      if (attentionBadge) {
        attentionBadge.style.display = content ? "inline-block" : "none";
      }

      bootstrap.Modal.getInstance(document.getElementById("attentionModal"))?.hide();
      showAlert("Anotação salva!", "success");
    } else {
      showAlert(result.error || "Erro ao salvar", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao salvar anotação", "danger");
  }
}

function openEditPatientModal() {
  new bootstrap.Modal(document.getElementById("editPatientModal")).show();
}

async function savePatientData() {
  const patientId = getPatientId();
  const data = {
    name: document.getElementById("editPatientName")?.value || "",
    email: document.getElementById("editPatientEmail")?.value || "",
    phone: document.getElementById("editPatientPhone")?.value || "",
    birth_date: document.getElementById("editPatientBirthDate")?.value || "",
    cpf: document.getElementById("editPatientCpf")?.value || "",
    address: document.getElementById("editPatientAddress")?.value || "",
    city: document.getElementById("editPatientCity")?.value || "",
    state: document.getElementById("editPatientState")?.value || "",
    zip_code: document.getElementById("editPatientZip")?.value || "",
    mother_name: document.getElementById("editPatientMotherName")?.value || "",
    occupation: document.getElementById("editPatientOccupation")?.value || "",
    indication_source: document.getElementById("editPatientIndication")?.value || "",
    patient_type: document.getElementById("editPatientType")?.value || "particular"
  };

  if (!data.name.trim()) {
    showAlert("Nome do paciente é obrigatório", "warning");
    return;
  }

  try {
    const result = await core.fetchJson(`/api/patient/${patientId}/update`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify(data)
    });

    if (result.success) {
      bootstrap.Modal.getInstance(document.getElementById("editPatientModal"))?.hide();
      showAlert("Dados do paciente atualizados!", "success");
      setTimeout(() => location.reload(), 800);
    } else {
      showAlert(result.error || "Erro ao atualizar", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao salvar dados", "danger");
  }
}

async function uploadPatientPhoto(input) {
  const patientId = getPatientId();
  if (!input.files || !input.files[0]) return;

  const file = input.files[0];
  if (file.size > 5 * 1024 * 1024) {
    showAlert("Arquivo muito grande. Máximo 5MB.", "warning");
    return;
  }

  const formData = new FormData();
  formData.append("photo", file);

  try {
    const response = await fetch(`/api/patient/${patientId}/photo`, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": getCSRFToken()
      },
      body: formData
    });

    const result = await response.json();
    if (result.success) {
      showAlert("Foto salva com sucesso!", "success");
      setTimeout(() => location.reload(), 500);
    } else {
      showAlert(result.error || "Erro ao salvar foto", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao enviar foto", "danger");
  }
}

async function deletePatientPhoto() {
  const patientId = getPatientId();
  if (!confirm("Remover foto do paciente?")) return;

  try {
    const result = await core.fetchJson(`/api/patient/${patientId}/photo`, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": getCSRFToken()
      }
    });

    if (result.success) {
      showAlert("Foto removida!", "success");
      setTimeout(() => location.reload(), 500);
    } else {
      showAlert(result.error || "Erro ao remover foto", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao remover foto", "danger");
  }
}

/* =========================
   TAGS
========================= */

async function savePatientTags() {
  const patientId = getPatientId();
  const selectedTags = Array.from(document.querySelectorAll(".tag-checkbox:checked"))
    .map((cb) => parseInt(cb.value, 10));

  try {
    const result = await core.fetchJson(`/api/patient/${patientId}/tags`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({ tags: selectedTags })
    });

    if (result.success) {
      showAlert("Tags atualizadas com sucesso!", "success");
    } else {
      showAlert(result.error || "Erro ao atualizar tags.", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao atualizar tags.", "danger");
  }
}

/* =========================
   TIMELINE ÚNICA
========================= */

function closeAllTimelinePopovers() {
  document.querySelectorAll(".timeline-popover").forEach((p) => {
    p.style.display = "none";
  });
}

function handleTimelineDotClick(dot) {
  const popover = dot.parentElement?.querySelector(".timeline-popover");
  if (!popover) return;

  const isVisible = popover.style.display === "block";
  closeAllTimelinePopovers();
  popover.style.display = isVisible ? "none" : "block";
}

function scrollToConsultation(id) {
  let el = document.getElementById(id);

  if (!el && typeof id === "string" && id.startsWith("consultation-")) {
    const legacyId = id.replace("consultation-", "consult-");
    el = document.getElementById(legacyId);
  }

  if (!el) return;

  const consultId = String(id).replace("consultation-", "");
  setCosmeticContextFromConsultation(consultId);

  const collapseEl =
    el.querySelector(".accordion-collapse") ||
    el.closest(".accordion-item")?.querySelector(".accordion-collapse");

  if (collapseEl && !collapseEl.classList.contains("show")) {
    const bsCollapse = new bootstrap.Collapse(collapseEl, { toggle: false });
    bsCollapse.show();
  }

  const historicoCard = el.closest(".card");
  if (historicoCard) {
    historicoCard.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  setTimeout(() => {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    el.classList.add("timeline-highlight");
    setTimeout(() => el.classList.remove("timeline-highlight"), 2000);
  }, 350);
}

function scrollToEvent(id, searchText = null) {
  const element = document.getElementById(id);
  if (element) {
    if (id.startsWith("consultation-")) {
      scrollToConsultation(id);
      return;
    }

    element.scrollIntoView({ behavior: "smooth", block: "center" });
    element.classList.add("highlight-consult");
    setTimeout(() => element.classList.remove("highlight-consult"), 2000);
    return;
  }

  if (searchText) {
    const items = document.querySelectorAll(".list-group-item, .consultation-card, .card");
    for (const item of items) {
      if (item.textContent.includes(searchText)) {
        item.scrollIntoView({ behavior: "smooth", block: "center" });
        item.classList.add("highlight-consult");
        setTimeout(() => item.classList.remove("highlight-consult"), 2000);
        break;
      }
    }
  }
}

async function recalculateEvolution(itemId) {
  if (!confirm("Deseja regerar o texto desta evolução com base nas notas?")) return;

  const tryUrls = [
    `/api/evolution/recalculate/${itemId}`,
    `/api/admin/recalculate-evolution/${itemId}`
  ];

  for (const url of tryUrls) {
    try {
      const result = await core.fetchJson(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken()
        }
      });

      if (result.success) {
        showAlert("Evolução regerada! Recarregando...", "success");
        setTimeout(() => location.reload(), 1000);
        return;
      }
    } catch (e) {
      console.warn("Falha ao regerar evolução em", url, e);
    }
  }

  showAlert("Erro ao regerar evolução", "danger");
}

/* =========================
   CATEGORIAS / LAYOUT
========================= */

function updateCategoryTexts() {
  const queixaText = document.getElementById("queixaText");
  const anamneseText = document.getElementById("anamneseText");
  const condutaText = document.getElementById("condutaText");

  if (currentCategory === "cosmiatria") {
    if (anamneseText && !anamneseText.value) {
      anamneseText.value =
        "Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.";
    }
  } else if (currentCategory === "transplante_capilar") {
    if (queixaText && !queixaText.value) {
      queixaText.value = "Paciente refere queixa de rarefação capilar e calvície progressiva.";
    }
    if (condutaText && !condutaText.value) {
      condutaText.value =
        "O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n";
    }
  }
}

function updateMainLayoutColumns(forceShow = false) {
  const left = document.getElementById("prontuarioLeftColumn");
  const right = document.getElementById("cosmeticRightColumn");

  if (!left || !right) return;

  // Desktop: painel sempre visível durante todo o atendimento.
  const isDesktop = window.matchMedia("(min-width: 1200px)").matches;
  const shouldShowMobile = forceShow || currentRightPanelMode !== null || !!currentCategory;

  left.classList.remove("col-lg-12");
  left.classList.add("col-lg-8");
  right.classList.add("col-lg-4");

  if (isDesktop || shouldShowMobile) {
    right.classList.remove("d-none");
  } else {
    right.classList.add("d-none");
  }
}

function toggleCategoryTabs() {
  const tabPlanejamento = document.getElementById("tabPlanejamento");
  const tabTransplante = document.getElementById("tabTransplante");
  const tabSurgery = document.getElementById("tabSurgery");
  const conductProcedures = document.getElementById("conductProceduresSection");
  const indicatedProcedures = document.getElementById("indicatedProceduresSection");

  if (tabPlanejamento) tabPlanejamento.style.display = "none";
  if (tabTransplante) tabTransplante.style.display = "none";
  if (tabSurgery) tabSurgery.style.display = "none";
  if (conductProcedures) conductProcedures.style.display = "none";
  if (indicatedProcedures) indicatedProcedures.style.display = "none";

  if (currentCategory === "cosmiatria") {
    if (tabPlanejamento) tabPlanejamento.style.display = "";
  } else if (currentCategory === "transplante_capilar") {
    if (tabTransplante) tabTransplante.style.display = "";
    if (tabSurgery) tabSurgery.style.display = "";
  } else {
    if (indicatedProcedures) indicatedProcedures.style.display = "";
  }

  updateMainLayoutColumns(currentCategory === "cosmiatria" || currentRightPanelMode !== null);
}

async function handleCategoryChange(event) {
  const newCategory = event.target.value;

  if ((newCategory === "cosmiatria" || newCategory === "transplante_capilar") && !timerStartTime) {
    startConsultation();
  }

  currentCategory = newCategory;

  if (currentCategory !== "cosmiatria") {
    clearCosmeticContext(false);
  }

  updateCategoryTexts();
  toggleCategoryTabs();

  if (currentCategory === "cosmiatria") {
    try {
      await loadExistingPlans();
    } catch (e) {
      console.warn("Falha ao carregar planejamento cosmético:", e);
    }
    renderCosmeticConduct();
    renderRightPanel("cosmiatria");
    showRightPanel();
    return;
  }

  if (currentCategory === "transplante_capilar") {
    renderTransplantRightPanelFromScreen();
    showRightPanel();
    return;
  }

  if (currentCategory === "patologia") {
    renderPatologiaRightPanelFromScreen();
    showRightPanel();
  }
}

function initCategoryFromCheckedRadio() {
  const checked = document.querySelector('input[name="category"]:checked');
  currentCategory = checked ? checked.value : "patologia";

  updateCategoryTexts();
  toggleCategoryTabs();

  if (currentCategory === "cosmiatria") {
    renderRightPanel("cosmiatria");
    showRightPanel();
  } else if (currentCategory === "transplante_capilar") {
    renderTransplantRightPanelFromScreen();
    showRightPanel();
  } else {
    renderPatologiaRightPanelFromScreen();
    showRightPanel();
  }
}

/* =========================
   COSMIATRIA - CONTEXTO INTELIGENTE
========================= */

function getProcedureContextKey(proc) {
  if (!proc) return "";

  if (hasValue(proc.consultationKey)) return `consultationKey:${normalizeString(proc.consultationKey)}`;
  if (hasValue(proc.appointmentId)) return `appointmentId:${normalizeString(proc.appointmentId)}`;
  if (hasValue(proc.consultationDate)) return `consultationDate:${normalizeString(proc.consultationDate)}`;

  return "sem-contexto";
}

function buildCosmeticContextFromConsultation(consultationId) {
  const id = normalizeString(consultationId);
  if (!id) return null;

  return {
    type: "consultation",
    key: `consultationKey:${id}`,
    consultationKey: id,
    appointmentId: id,
    label: `Consulta ${id}`
  };
}

function setCosmeticContext(context, rerender = true) {
  activeCosmeticContext = context || null;
  if (rerender) renderCosmeticConduct();
}

function clearCosmeticContext(rerender = true) {
  activeCosmeticContext = null;
  if (rerender) renderCosmeticConduct();
}

function setCosmeticContextFromConsultation(consultationId) {
  if (currentCategory !== "cosmiatria") return;

  const id = normalizeString(consultationId);
  if (!id) return;

  activeCosmeticContext = {
    type: "consultation",
    consultationKey: id,
    appointmentId: id,
    fallbackConsultationKey: `note_${id}`,
    label: `Consulta ${id}`
  };

  renderCosmeticConduct();
}

function matchesContext(proc, context) {
  if (!context) return true;
  if (!proc) return false;

  const procConsultationKey = normalizeString(proc.consultationKey);
  const procAppointmentId = normalizeString(proc.appointmentId);
  const procConsultationDate = normalizeString(proc.consultationDate);

  const ctxConsultationKey = normalizeString(context.consultationKey);
  const ctxAppointmentId = normalizeString(context.appointmentId);
  const ctxFallbackConsultationKey = normalizeString(context.fallbackConsultationKey);
  const ctxConsultationDate = normalizeString(context.consultationDate);

  if (ctxConsultationKey && procConsultationKey && procConsultationKey === ctxConsultationKey) return true;
  if (ctxConsultationKey && procAppointmentId && procAppointmentId === ctxConsultationKey) return true;

  if (ctxAppointmentId && procAppointmentId && procAppointmentId === ctxAppointmentId) return true;
  if (ctxAppointmentId && procConsultationKey && procConsultationKey === ctxAppointmentId) return true;

  if (ctxFallbackConsultationKey && procConsultationKey && procConsultationKey === ctxFallbackConsultationKey) return true;
  if (ctxFallbackConsultationKey && procAppointmentId && procAppointmentId === ctxFallbackConsultationKey) return true;

  if (ctxConsultationDate && procConsultationDate && procConsultationDate === ctxConsultationDate) return true;

  return false;
}

function getPlansForCurrentContext() {
  if (!activeCosmeticContext) {
    return cosmeticPlans.slice();
  }
  return cosmeticPlans.filter((plan) => matchesContext(plan, activeCosmeticContext));
}

function getPlanExecutions(planId) {
  return planExecutionsByPlanId[String(planId)] || [];
}

function getPlanPerformed(plan) {
  return getPlanExecutions(plan.id).some((execution) => (execution.execution_status || (execution.was_performed ? "realizada" : "agendada")) === "realizada");
}

function getPlanRealizedValue(plan) {
  return getPlanExecutions(plan.id)
    .filter((execution) => (execution.execution_status || (execution.was_performed ? "realizada" : "agendada")) === "realizada")
    .reduce((sum, execution) => sum + (parseFloat(execution.charged_value) || 0), 0);
}

function buildCosmeticSummary(procs) {
  const planned = procs.reduce((sum, plan) => sum + (parseFloat(plan.budget ?? plan.value) || 0), 0);
  const realized = procs.reduce((sum, plan) => sum + getPlanRealizedValue(plan), 0);
  const realizedItems = procs.filter((plan) => getPlanPerformed(plan));
  const pendingItems = procs.filter((plan) => !getPlanPerformed(plan));

  return {
    planned,
    realized,
    pendingCount: pendingItems.length,
    performedCount: realizedItems.length,
    totalCount: procs.length
  };
}

function groupProceduresForPanel(procs) {
  const map = new Map();

  procs.forEach((proc) => {
    const key = getProcedureContextKey(proc);
    if (!map.has(key)) {
      map.set(key, {
        key,
        title: proc.consultationDate || "Planejamento atual",
        procedures: []
      });
    }
    map.get(key).procedures.push(proc);
  });

  return Array.from(map.values());
}

function renderCosmeticSummaryCards(summary, contextLabel) {
  return `
    <div class="mb-3">
      <div class="d-flex align-items-start justify-content-between gap-2">
        <div>
          <h5 class="fw-bold mb-1 text-success">
            <i class="bi bi-heart-pulse me-2"></i>Painel Cosmiatria
          </h5>
          <div class="small text-muted">${core.escapeHtml(contextLabel)}</div>
        </div>
        ${
          activeCosmeticContext
            ? `<button class="btn btn-sm btn-outline-secondary" onclick="clearCosmeticContext()">
                 <i class="bi bi-arrow-counterclockwise me-1"></i>Visão geral
               </button>`
            : ""
        }
      </div>
    </div>

    <div class="row g-2 mb-3">
      <div class="col-6">
        <div class="card border-0 bg-light h-100">
          <div class="card-body py-2 px-3">
            <div class="text-muted small">Planejado</div>
            <div class="fw-bold text-primary">R$ ${formatMoneyBRL(summary.planned)}</div>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="card border-0 bg-light h-100">
          <div class="card-body py-2 px-3">
            <div class="text-muted small">Realizado</div>
            <div class="fw-bold text-success">R$ ${formatMoneyBRL(summary.realized)}</div>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="card border-0 bg-light h-100">
          <div class="card-body py-2 px-3">
            <div class="text-muted small">Pendentes</div>
            <div class="fw-bold text-danger">${summary.pendingCount}</div>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="card border-0 bg-light h-100">
          <div class="card-body py-2 px-3">
            <div class="text-muted small">Procedimentos</div>
            <div class="fw-bold">${summary.totalCount}</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderProcedureCard(proc) {
  const value = parseFloat(proc.budget ?? proc.value) || 0;
  const executions = getPlanExecutions(proc.id);
  const lastExecution = executions[0] || null;
  const performed = getPlanPerformed(proc);
  const followupText = lastExecution
    ? `${lastExecution.followup_date ? formatDateBR(lastExecution.followup_date) : "-"} · ${lastExecution.followup_status || "pendente"}`
    : "-";
  const iconClass = performed
    ? "bi-check-circle-fill text-success"
    : "bi-x-circle-fill text-danger";

  return `
    <div class="card mb-2 border-0 shadow-sm ${performed ? "opacity-75" : ""}">
      <div class="card-body py-3 px-3">
        <div class="d-flex align-items-start justify-content-between gap-2">
          <div class="flex-grow-1">
            <div class="d-flex align-items-start gap-2">
              <i class="bi ${iconClass} fs-5 mt-1"></i>
              <div>
                <div class="fw-bold ${performed ? "text-muted" : "text-dark"}">${core.escapeHtml(proc.name)}</div>
                <div class="text-muted">R$ ${formatMoneyBRL(value)} · ${executions.length} sessão(ões)</div>
                <div class="small text-muted mt-1">Follow-up (última sessão): ${core.escapeHtml(followupText)}</div>
              </div>
            </div>
          </div>
          <div class="d-flex gap-1">
            ${!performed ? `<button class="btn btn-sm btn-outline-success py-1 px-2" title="Marcar como realizado" onclick="performCosmeticProcedure(${proc.id}, '${core.escapeHtml(proc.name)}')">
              <i class="bi bi-check-lg"></i>
            </button>` : ''}
            <button class="btn btn-sm btn-outline-danger py-1 px-2" title="Deletar planejamento" onclick="deleteCosmeticPlan(${proc.id}, '${core.escapeHtml(proc.name)}')">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function parseCurrencyInputToFloat(value) {
  if (value === null || value === undefined) return 0;
  const numeric = String(value)
    .replace(/\s/g, "")
    .replace(/\./g, "")
    .replace(",", ".")
    .replace(/[^\d.-]/g, "");
  return parseFloat(numeric) || 0;
}

function updateProcedureValueFromCurrencyInput(index, rawValue, inputEl = null) {
  const value = parseCurrencyInputToFloat(rawValue);
  updatePlanValue(index, value);

  if (inputEl) {
    inputEl.value = value.toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }
}

function renderCosmeticConduct() {
  const rightColumn = document.getElementById("cosmeticRightColumn");
  const rightContent = document.getElementById("clinicalRightPanel");
  const panelTitle = document.getElementById("cosmeticRightColumnTitle");

  if (!rightColumn || !rightContent) return;

  currentRightPanelMode = "cosmiatria";
  if (panelTitle) {
    panelTitle.innerHTML = '<i class="bi bi-heart-pulse me-2"></i>Planejamento e Execução';
  }

  const shouldShow =
    currentCategory === "cosmiatria" &&
    Array.isArray(cosmeticPlans);

  if (!shouldShow || cosmeticPlans.length === 0) {
    rightContent.innerHTML = '<div class="text-muted small">Nenhum procedimento planejado.</div>';
    showRightPanel();
    return;
  }

  const procs = getPlansForCurrentContext();
  const contextLabel = activeCosmeticContext
    ? "Consulta em foco"
    : "Visão geral de todos os planejamentos";

  if (!procs.length) {
    rightContent.innerHTML = `
      ${renderCosmeticSummaryCards(buildCosmeticSummary([]), contextLabel)}
      <div class="text-muted small">Nenhum procedimento encontrado para este contexto.</div>
      ${
        activeCosmeticContext
          ? `<div class="mt-3">
               <button class="btn btn-sm btn-outline-secondary" onclick="clearCosmeticContext()">
                 <i class="bi bi-arrow-counterclockwise me-1"></i>Voltar para visão geral
               </button>
             </div>`
          : ""
      }
    `;
    showRightPanel();
    return;
  }

  let html = renderCosmeticSummaryCards(buildCosmeticSummary(procs), contextLabel);

  if (activeCosmeticContext) {
    const sortedProcs = [...procs].sort((a, b) => {
      if (getPlanPerformed(a) === getPlanPerformed(b)) return 0;
      return getPlanPerformed(a) ? 1 : -1;
    });

    sortedProcs.forEach((proc) => {
      html += renderProcedureCard(proc);
    });
  } else {
    const grouped = groupProceduresForPanel(procs);

    grouped.forEach((group) => {
      const sorted = [...group.procedures].sort((a, b) => {
        if (a.performed === b.performed) return 0;
        return a.performed ? 1 : -1;
      });

      html += `
        <div class="mt-3 mb-2 border-top pt-3">
          <div class="d-flex align-items-center justify-content-between">
            <div class="fw-bold text-secondary">
              <i class="bi bi-calendar3 me-2"></i>${core.escapeHtml(group.title)}
            </div>
          </div>
        </div>
      `;

      sorted.forEach((proc) => {
        html += renderProcedureCard(proc);
      });
    });
  }

  const total = procs.reduce(
    (sum, proc) => sum + (parseFloat(proc.budget ?? proc.value) || 0),
    0
  );

  html += `
    <div class="mt-3 p-3 bg-light rounded shadow-sm">
      <div class="fw-bold">
        Total do painel: <span class="text-primary">R$ ${formatMoneyBRL(total)}</span>
      </div>
    </div>
  `;

  rightContent.innerHTML = html;
  showRightPanel();
}

/* =========================
   PAINEL LATERAL UNIVERSAL
========================= */

function showRightPanel() {
  updateMainLayoutColumns(true);
}

function hideRightPanel() {
  currentRightPanelMode = null;
  currentHistoricalConsultation = null;
  // Mantém coluna no desktop; apenas permite ocultar no mobile quando necessário.
  updateMainLayoutColumns(false);
}

function renderPatologiaRightPanelFromScreen() {
  const panelTitle = document.getElementById("cosmeticRightColumnTitle");
  const panelContent = document.getElementById("clinicalRightPanel");
  if (!panelContent) return;

  currentRightPanelMode = "patologia";

  if (panelTitle) {
    panelTitle.innerHTML = '<i class="bi bi-journal-text me-2"></i>Observações';
  }

  const queixa = document.getElementById("queixaText")?.value || "";
  const diagnostico = document.getElementById("diagnosticoText")?.value || "";
  const conduta = document.getElementById("condutaText")?.value || "";

  panelContent.innerHTML = `
    <div class="card border-0 bg-light">
      <div class="card-body small">
        <div class="mb-3">
          <div class="fw-bold text-primary mb-1">Queixa</div>
          <div style="white-space: pre-wrap;">${core.escapeHtml(queixa || "-")}</div>
        </div>
        <div class="mb-3">
          <div class="fw-bold text-primary mb-1">Diagnóstico</div>
          <div style="white-space: pre-wrap;">${core.escapeHtml(diagnostico || "-")}</div>
        </div>
        <div>
          <div class="fw-bold text-primary mb-1">Conduta</div>
          <div style="white-space: pre-wrap;">${core.escapeHtml(conduta || "-")}</div>
        </div>
      </div>
    </div>
  `;

  showRightPanel();
}

function renderTransplantRightPanelFromScreen() {
  const panelTitle = document.getElementById("cosmeticRightColumnTitle");
  const panelContent = document.getElementById("clinicalRightPanel");
  if (!panelContent) return;

  currentRightPanelMode = "transplante";

  if (panelTitle) {
    panelTitle.innerHTML = '<i class="bi bi-scissors me-2"></i>Planejamento Cirúrgico';
  }

  const planning = buildSurgicalPlanningPayload();
  const boolText = (v) => (v ? "Sim" : "Não");

  panelContent.innerHTML = `
    <div class="card border-0 bg-light">
      <div class="card-body small">
        <div class="mb-2"><strong>Norwood:</strong> ${core.escapeHtml(planning.norwood || "-")}</div>
        <div class="mb-2"><strong>Transplante anterior:</strong> ${core.escapeHtml(planning.previous_transplant || "-")}</div>
        <div class="mb-2"><strong>Local:</strong> ${core.escapeHtml(planning.transplant_location || "-")}</div>
        <div class="mb-2"><strong>Tipo de caso:</strong> ${core.escapeHtml(planning.case_type || "-")}</div>
        <div class="mb-2"><strong>Body hair:</strong> ${boolText(planning.body_hair_needed)}</div>
        <div class="mb-2"><strong>Sobrancelha:</strong> ${boolText(planning.eyebrow_transplant)}</div>
        <div class="mb-2"><strong>Barba:</strong> ${boolText(planning.beard_transplant)}</div>
        <div class="mb-2"><strong>Feminino:</strong> ${boolText(planning.feminine_hair_transplant)}</div>
        <div class="mb-2"><strong>Frontal:</strong> ${boolText(planning.frontal)}</div>
        <div class="mb-2"><strong>Coroa:</strong> ${boolText(planning.crown)}</div>
        <div class="mb-2"><strong>Completo:</strong> ${boolText(planning.complete)}</div>
        <div class="mb-2"><strong>Completo + body hair:</strong> ${boolText(planning.complete_body_hair)}</div>
        <div class="mb-2"><strong>Dense packing:</strong> ${boolText(planning.dense_packing)}</div>

        <hr>

        <div class="mb-2 fw-bold text-primary">Planejamento</div>
        <div style="white-space: pre-wrap;">${core.escapeHtml(planning.surgical_planning_text || "-")}</div>

        <hr>

        <div class="mb-2 fw-bold text-primary">Conduta clínica</div>
        <div style="white-space: pre-wrap;">${core.escapeHtml(planning.clinical_conduct || "-")}</div>
      </div>
    </div>
  `;

  showRightPanel();
}

function renderHistoricalConsultationRightPanel(consultationId, category) {
  const consultationCard = document.getElementById(`consultation-${consultationId}`);
  const panelTitle = document.getElementById("cosmeticRightColumnTitle");
  const panelContent = document.getElementById("clinicalRightPanel");

  if (!consultationCard || !panelContent) return;

  currentHistoricalConsultation = consultationId;

  if (category === "cosmiatria") {
    currentRightPanelMode = "cosmiatria";

    if (panelTitle) {
      panelTitle.innerHTML = '<i class="bi bi-heart-pulse me-2"></i>Planejamento e Execução';
    }

    // Garante que o painel use o mesmo motor oficial da cosmiatria
    currentCategory = "cosmiatria";

    // Se ainda não houver dados carregados, tenta carregar antes de renderizar
    if (!Array.isArray(cosmeticPlans) || cosmeticPlans.length === 0) {
      panelContent.innerHTML = `<div class="text-muted small">Nenhum planejamento encontrado nesta consulta.</div>`;
      showRightPanel();
      return;
    }

    // Foca a consulta histórica específica no painel lateral
    activeCosmeticContext = {
      type: "consultation",
      consultationKey: String(consultationId),
      appointmentId: String(consultationId),
      fallbackConsultationKey: `note_${String(consultationId)}`,
      label: `Consulta ${consultationId}`
    };

    renderCosmeticConduct();
    showRightPanel();
    return;
  }

  if (category === "transplante_capilar") {
    currentRightPanelMode = "transplante";
    if (panelTitle) {
      panelTitle.innerHTML = '<i class="bi bi-scissors me-2"></i>Planejamento Cirúrgico';
    }

    const wrapper = consultationCard.querySelector(".js-surgical-plan-wrapper");
    if (!wrapper) {
      panelContent.innerHTML = `<div class="text-muted small">Nenhum planejamento cirúrgico encontrado nesta consulta.</div>`;
      showRightPanel();
      return;
    }

    panelContent.innerHTML = wrapper.outerHTML;
    showRightPanel();
    return;
  }

  currentRightPanelMode = "patologia";
  if (panelTitle) {
    panelTitle.innerHTML = '<i class="bi bi-journal-text me-2"></i>Observações';
  }

  const blocks = [];
  Array.from(consultationCard.querySelectorAll(".accordion-body .mb-3")).forEach((block) => {
    const text = block.textContent || "";
    if (
      text.includes("Queixa Principal") ||
      text.includes("Anamnese / Exame Físico") ||
      text.includes("Diagnóstico") ||
      text.includes("Conduta")
    ) {
      blocks.push(block.outerHTML);
    }
  });

  panelContent.innerHTML = blocks.length
    ? blocks.join("")
    : `<div class="text-muted small">Nenhum conteúdo encontrado nesta consulta.</div>`;

  showRightPanel();
}

function renderRightPanel(contextCategory = null, consultationData = null) {
  const panel = document.getElementById("cosmeticRightColumn");
  const panelContent = document.getElementById("clinicalRightPanel");
  const panelTitle = document.getElementById("cosmeticRightColumnTitle");

  if (!panel || !panelContent) return;

  const category = contextCategory || currentCategory || "patologia";
  panel.classList.remove("d-none");

  if (category === "cosmiatria") {
    currentRightPanelMode = "cosmiatria";

    if (panelTitle) panelTitle.innerHTML = '<i class="bi bi-heart-pulse me-2"></i>Planejamento e Execução';

    if (!Array.isArray(cosmeticPlans) || cosmeticPlans.length === 0) {
      panelContent.innerHTML = `<div class="text-muted small">Nenhum planejamento cadastrado.</div>`;
      showRightPanel();
      return;
    }

    renderCosmeticConduct();
    return;
  }

  if (category === "transplante_capilar") {
    currentRightPanelMode = "transplante";

    if (panelTitle) panelTitle.innerHTML = '<i class="bi bi-scissors me-2"></i>Planejamento Cirúrgico';

    if (!consultationData || !consultationData.surgical_planning) {
      renderTransplantRightPanelFromScreen();
      return;
    }

    const p = consultationData.surgical_planning;
    panelContent.innerHTML = `
      <div class="card border-0 bg-light">
        <div class="card-body small">
          <div><b>Norwood:</b> ${core.escapeHtml(p.norwood || "-")}</div>
          <div><b>Área:</b> ${core.escapeHtml(p.area || "-")}</div>
          <div><b>Técnica:</b> ${core.escapeHtml(p.technique || "-")}</div>
          <div><b>Body Hair:</b> ${p.body_hair ? "Sim" : "Não"}</div>
          <div><b>Dense Packing:</b> ${p.dense_packing ? "Sim" : "Não"}</div>
          <hr>
          <div style="white-space: pre-wrap;">${core.escapeHtml(p.description || "")}</div>
        </div>
      </div>
    `;
    showRightPanel();
    return;
  }

  // Fallback explícito: patologia (nunca esconde o painel no desktop).
  renderPatologiaRightPanelFromScreen();
}

function resolveHistoryCategoryFromBadgeText(categoryText) {
  const txt = String(categoryText || "").trim().toLowerCase();
  if (txt.includes("cosmiatria")) return "cosmiatria";
  if (txt.includes("transplante")) return "transplante_capilar";
  return "patologia";
}

function initializeRightPanelFromHistory() {
  const historyButtons = Array.from(document.querySelectorAll(".accordion-button[data-consultation-key]"));

  // Sem histórico: mantém painel visível e coerente com categoria atual.
  if (!historyButtons.length) {
    renderRightPanel(currentCategory || "patologia");
    return;
  }

  // Estratégia previsível: primeiro item renderizado no histórico (ordem do backend).
  const firstButton = historyButtons[0];
  const consultationKey = firstButton.getAttribute("data-consultation-key");
  const badge = firstButton.querySelector(".badge.bg-primary");
  const historyCategory = resolveHistoryCategoryFromBadgeText(badge ? badge.textContent : "");

  if (historyCategory) {
    currentCategory = historyCategory;
    const categoryInput = document.querySelector(`input[name="category"][value="${historyCategory}"]`);
    if (categoryInput) categoryInput.checked = true;
    toggleCategoryTabs();
  }

  if (consultationKey) {
    renderHistoricalConsultationRightPanel(consultationKey, historyCategory);
    return;
  }

  renderRightPanel(historyCategory);
}

/* =========================
   COSMIATRIA - DADOS
========================= */


function renderDateBucketPanel(targetId, buckets, emptyMessage) {
  const panel = document.getElementById(targetId);
  if (!panel) return;
  const dates = Object.keys(buckets || {}).filter(Boolean).sort((a, b) => b.localeCompare(a));
  if (!dates.length) {
    panel.innerHTML = `<span class="text-muted">${emptyMessage}</span>`;
    return;
  }

  panel.innerHTML = dates.map((dateKey) => {
    const items = buckets[dateKey] || [];
    const labels = items.map((item) => {
      const color = item.color || '#6c757d';
      const name = core.escapeHtml(item.procedure_name || item.name || 'Procedimento');
      return `<span class="badge me-1 mb-1" style="background:${color};">${name}</span>`;
    }).join('');
    return `
      <div class="mb-2">
        <div class="fw-bold">${formatDateBR(`${dateKey}T00:00:00`)}</div>
        <div>${labels || '<span class="text-muted">Sem itens</span>'}</div>
      </div>
    `;
  }).join('');
}

function renderPlanDateClusters() {
  renderDateBucketPanel('pendingByDatePanel', pendingByDateMap, 'Nenhum pendente.');
  renderDateBucketPanel('realizedByDatePanel', realizedByDateMap, 'Nenhum realizado.');
}
async function loadExistingPlans() {
  const patientId = getPatientId();
  if (!patientId) return;

  try {
    const data = await core.fetchJson(`/api/prontuario/${patientId}/cosmetic-plans-grouped`);

    groupedCosmeticPlans = [];
    cosmeticPlans = [];
    planExecutionsByPlanId = {};
    pendingByDateMap = {};
    realizedByDateMap = {};

    if (data.success && data.grouped_plans && data.grouped_plans.length > 0) {
      groupedCosmeticPlans = data.grouped_plans;
      pendingByDateMap = data.pending_by_date || {};
      realizedByDateMap = data.realized_by_date || {};

      data.grouped_plans.forEach((group) => {
        group.procedures.forEach((plan) => {
          const normalizedPlan = {
            id: plan.id,
            name: plan.procedure_name,
            value: parseFloat(plan.planned_value) || 0,
            months: plan.follow_up_months || 6,
            budget: parseFloat(plan.final_budget || plan.planned_value) || 0,
            observations: plan.observations || "",
            observation: plan.observations || "",
            status: plan.status || "ativo",
            consultationKey: group.consultation_key || null,
            consultationDate: group.consultation_info?.display_date || "",
            appointmentId: group.consultation_info?.appointment_id || null
          };

          cosmeticPlans.push(normalizedPlan);
          planExecutionsByPlanId[String(plan.id)] = Array.isArray(plan.executions) ? plan.executions : [];
        });
      });
    }

    renderCosmeticProcedures();
    renderPlanDateClusters();
    renderCosmeticConduct();
    updateCosmeticTotal();
    updateMainLayoutColumns();
  } catch (error) {
    console.error("Erro ao carregar planejamentos:", error);
    groupedCosmeticPlans = [];
    cosmeticPlans = [];
    planExecutionsByPlanId = {};
    pendingByDateMap = {};
    realizedByDateMap = {};
    renderCosmeticProcedures();
    renderPlanDateClusters();
    renderCosmeticConduct();
    updateCosmeticTotal();
    updateMainLayoutColumns();
  }
}

function updateCosmeticTotal() {
  const total = cosmeticPlans.reduce(
    (sum, proc) => sum + (parseFloat(proc.budget ?? proc.value) || 0),
    0
  );

  const totalEl = document.getElementById("cosmeticTotal");
  if (totalEl) totalEl.textContent = formatMoneyBRL(total);
}

function addCosmeticProcedure() {
  const nameInput = document.getElementById("newProcedureName");
  const valueInput = document.getElementById("newProcedureValue");
  const monthsInput = document.getElementById("newProcedureMonths");
  const observationsInput = document.getElementById("newProcedureObservations");

  const name = (nameInput?.value || "").trim();
  const value = parseFloat((valueInput?.value || "").trim()) || 0;
  const months = parseInt(monthsInput?.value || "6", 10) || 6;
  const observations = observationsInput?.value || "";

  if (!name) {
    alert("Por favor, selecione um procedimento");
    nameInput?.focus();
    return;
  }

  if (value <= 0) {
    alert("Por favor, informe um valor válido (maior que 0)");
    valueInput?.focus();
    return;
  }

  if (editingCosmeticProcedureIndex !== null) {
    const original = cosmeticPlans[editingCosmeticProcedureIndex];
    cosmeticPlans[editingCosmeticProcedureIndex] = {
      ...original,
      name,
      value,
      months,
      budget: parseFloat(original?.budget ?? value) || value,
      observations,
      observation: observations
    };
    editingCosmeticProcedureIndex = null;

    const addBtn = document.querySelector('[data-action="add-cosmetic-procedure"]');
    if (addBtn) {
      addBtn.innerHTML = '<i class="bi bi-plus-circle"></i> Adicionar';
      addBtn.classList.remove("btn-primary");
      addBtn.classList.add("btn-success");
    }

    showAlert("Procedimento atualizado com sucesso.", "success");
  } else {
    cosmeticPlans.push({
      name,
      value,
      months,
      budget: value,
      observations,
      observation: observations
    });
    showAlert("Procedimento adicionado com sucesso.", "success");
  }

  renderCosmeticProcedures();
  renderCosmeticConduct();
  updateCosmeticTotal();
  updateMainLayoutColumns();

  if (nameInput) nameInput.value = "";
  if (valueInput) valueInput.value = "";
  if (monthsInput) monthsInput.value = "6";
  if (observationsInput) observationsInput.value = "";

  setTimeout(() => nameInput?.focus(), 100);
}

function editCosmeticProcedure(index) {
  const proc = cosmeticPlans[index];
  if (!proc) return;

  editingCosmeticProcedureIndex = index;

  document.getElementById("newProcedureName").value = proc.name || "";
  document.getElementById("newProcedureValue").value = proc.value || 0;
  document.getElementById("newProcedureMonths").value = proc.months || 6;
  document.getElementById("newProcedureObservations").value =
    proc.observations || proc.observation || "";

  const addBtn = document.querySelector('[data-action="add-cosmetic-procedure"]');
  if (addBtn) {
    addBtn.innerHTML = '<i class="bi bi-check-circle"></i> Salvar Edição';
    addBtn.classList.remove("btn-success");
    addBtn.classList.add("btn-primary");
  }

  document.getElementById("newProcedureName")?.focus();
  showAlert("Procedimento carregado para edição.", "info");
}

function removeCosmeticProcedure(index) {
  cosmeticPlans.splice(index, 1);

  if (editingCosmeticProcedureIndex === index) {
    editingCosmeticProcedureIndex = null;

    const addBtn = document.querySelector('[data-action="add-cosmetic-procedure"]');
    if (addBtn) {
      addBtn.innerHTML = '<i class="bi bi-plus-circle"></i> Adicionar';
      addBtn.classList.remove("btn-primary");
      addBtn.classList.add("btn-success");
    }

    document.getElementById("newProcedureName").value = "";
    document.getElementById("newProcedureValue").value = "";
    document.getElementById("newProcedureMonths").value = "6";
    document.getElementById("newProcedureObservations").value = "";
  }

  renderCosmeticProcedures();
  renderCosmeticConduct();
  updateCosmeticTotal();
  updateMainLayoutColumns();
}

function updatePlanValue(index, val) {
  if (!cosmeticPlans[index]) return;
  cosmeticPlans[index].budget = parseFloat(val) || 0;
  cosmeticPlans[index].value = parseFloat(val) || 0;
  updateCosmeticTotal();
  renderCosmeticConduct();
}


function updatePlanDate() {
  showAlert("No novo fluxo, datas são controladas por sessão.", "info");
}

function togglePlanPerformed() {
  showAlert("No novo fluxo, realizado é controlado por sessão.", "info");
}

async function updatePlanStatus(planId, status) {
  try {
    const result = await core.fetchJson(`/api/prontuario/cosmetic-plan/${planId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
      body: JSON.stringify({ status })
    });
    if (!result.success) {
      showAlert(result.error || "Erro ao atualizar status", "danger");
      return;
    }
    await loadExistingPlans();
  } catch (error) {
    console.error(error);
    showAlert("Erro ao atualizar status do plano", "danger");
  }
}

async function createExecution(planId, payload) {
  return core.fetchJson(`/api/cosmetic-plans/${planId}/executions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
    body: JSON.stringify(payload)
  });
}

async function updateExecution(executionId, payload) {
  return core.fetchJson(`/api/executions/${executionId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
    body: JSON.stringify(payload)
  });
}

async function deleteExecution(executionId) {
  return core.fetchJson(`/api/executions/${executionId}`, {
    method: "DELETE",
    headers: { "X-CSRFToken": getCSRFToken() }
  });
}

async function promptCreateExecution(planId) {
  const execution_status = (prompt("Status da sessão (agendada, realizada, cancelada, faltou)", "agendada") || "agendada").toLowerCase();
  const scheduled_date = prompt("Data agendada (AAAA-MM-DD)", "") || null;
  const performed_date = prompt("Data realizada (AAAA-MM-DD)", "") || null;
  const charged_raw = prompt("Valor cobrado (R$)", "") || "";
  const notes = prompt("Observações", "") || "";
  const followup_date = prompt("Data follow-up (AAAA-MM-DD)", "") || null;

  const payload = {
    scheduled_date,
    performed_date,
    execution_status,
    charged_value: charged_raw ? parseFloat(String(charged_raw).replace(',', '.')) : null,
    notes,
    followup_date,
    followup_status: "pendente"
  };

  try {
    const result = await createExecution(planId, payload);
    if (!result.success) {
      showAlert(result.error || "Erro ao registrar sessão", "danger");
      return;
    }
    await loadExistingPlans();
    showAlert("Sessão registrada com sucesso", "success");
  } catch (error) {
    console.error(error);
    showAlert("Erro ao criar sessão", "danger");
  }
}

async function promptEditExecution(executionId) {
  const entry = Object.values(planExecutionsByPlanId).flat().find((e) => Number(e.id) === Number(executionId));
  if (!entry) return;

  const execution_status = (prompt("Status da sessão (agendada, realizada, cancelada, faltou)", entry.execution_status || (entry.was_performed ? "realizada" : "agendada")) || "agendada").toLowerCase();
  const scheduled_date = prompt("Data agendada (AAAA-MM-DD)", entry.scheduled_date ? String(entry.scheduled_date).slice(0, 10) : "") || null;
  const performed_date = prompt("Data realizada (AAAA-MM-DD)", entry.performed_date ? String(entry.performed_date).slice(0, 10) : "") || null;
  const charged_raw = prompt("Valor cobrado (R$)", entry.charged_value ?? "") || "";
  const notes = prompt("Observações", entry.notes || "") || "";

  try {
    const result = await updateExecution(executionId, {
      performed_date,
      execution_status,
      charged_value: charged_raw ? parseFloat(String(charged_raw).replace(',', '.')) : null,
      notes
    });
    if (!result.success) {
      showAlert(result.error || "Erro ao editar sessão", "danger");
      return;
    }
    await loadExistingPlans();
    showAlert("Sessão atualizada", "success");
  } catch (error) {
    console.error(error);
    showAlert("Erro ao atualizar sessão", "danger");
  }
}

async function removePlan(planId) {
  if (!confirm("Excluir este planejamento e todas as sessões?")) return;
  try {
    const result = await core.fetchJson(`/api/prontuario/cosmetic-plan/${planId}`, {
      method: "DELETE",
      headers: { "X-CSRFToken": getCSRFToken() }
    });
    if (!result.success) {
      showAlert(result.error || "Erro ao excluir planejamento", "danger");
      return;
    }
    await loadExistingPlans();
    showAlert("Planejamento excluído", "success");
  } catch (error) {
    console.error(error);
    showAlert("Erro ao excluir planejamento", "danger");
  }
}

async function removeExecution(executionId) {
  if (!confirm("Excluir esta sessão?")) return;
  try {
    const result = await deleteExecution(executionId);
    if (!result.success) {
      showAlert(result.error || "Erro ao excluir sessão", "danger");
      return;
    }
    await loadExistingPlans();
  } catch (error) {
    console.error(error);
    showAlert("Erro ao excluir sessão", "danger");
  }
}

function renderExecutionRow(tbody, execution) {
  const row = tbody.insertRow();
  row.className = "table-light";
  row.innerHTML = `
    <td></td>
    <td class="small">${execution.scheduled_date ? formatDateBR(execution.scheduled_date) : "-"}</td>
    <td class="small">${execution.performed_date ? formatDateBR(execution.performed_date) : "-"}<div class="text-muted">${core.escapeHtml(execution.execution_status || (execution.was_performed ? "realizada" : "agendada"))}</div></td>
    <td class="small">${execution.charged_value !== null && execution.charged_value !== undefined ? formatMoneyBRL(execution.charged_value) : "-"}</td>
    <td class="small">${core.escapeHtml(execution.notes || "-")}</td>
    <td class="small">${execution.followup_date ? formatDateBR(execution.followup_date) : "-"} · ${core.escapeHtml(execution.followup_status || "pendente")}</td>
    <td class="text-center">
      <button class="btn btn-sm btn-outline-primary border-0" onclick="promptEditExecution(${execution.id})"><i class="bi bi-pencil"></i></button>
      <button class="btn btn-sm btn-outline-danger border-0" onclick="removeExecution(${execution.id})"><i class="bi bi-trash"></i></button>
    </td>
  `;
}

function renderCosmeticProcedures() {
  const tbody = document.getElementById("cosmeticPlanBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  cosmeticPlans.forEach((plan, index) => {
    const executions = getPlanExecutions(plan.id);
    const performed = getPlanPerformed(plan);
    const expanded = expandedCosmeticPlans.has(plan.id);
    const row = tbody.insertRow();
    row.className = performed ? "table-success" : "";
    row.innerHTML = `
      <td class="ps-2"><div class="fw-bold">${core.escapeHtml(plan.name)}</div></td>
      <td><input type="number" class="form-control form-control-sm" value="${plan.budget || plan.value}" onchange="updatePlanValue(${index}, this.value)"></td>
      <td><input type="number" class="form-control form-control-sm" value="${plan.months || 6}" readonly></td>
      <td>
        <select class="form-select form-select-sm" onchange="updatePlanStatus(${plan.id}, this.value)">
          ${['ativo','pausado','concluido','cancelado'].map((st)=>`<option value="${st}" ${plan.status===st?'selected':''}>${st}</option>`).join('')}
        </select>
      </td>
      <td class="text-center">
        <button class="btn btn-sm btn-outline-secondary" onclick="togglePlanSessions(${plan.id})">Sessões (${executions.length})</button>
        <button class="btn btn-sm btn-outline-success" onclick="promptCreateExecution(${plan.id})">Registrar nova sessão</button>
        <button class="btn btn-sm btn-outline-danger" onclick="removePlan(${plan.id})">Excluir planejamento</button>
      </td>
    `;

    if (expanded) {
      executions.forEach((execution) => renderExecutionRow(tbody, execution));
    }
  });

  if (cosmeticPlans.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-3">Nenhum procedimento planejado</td></tr>';
  }
}

function togglePlanSessions(planId) {
  if (expandedCosmeticPlans.has(planId)) {
    expandedCosmeticPlans.delete(planId);
  } else {
    expandedCosmeticPlans.add(planId);
  }
  renderCosmeticProcedures();
}

async function performCosmeticProcedure(planId, procedureName, consultationId = null) {
  const today = new Date().toISOString().split("T")[0];
  const dateInput = prompt(`Marcar "${procedureName}" como realizado em qual data? (AAAA-MM-DD)`, today);
  if (!dateInput) return;

  await promptCreateExecution(planId);
}

async function deleteCosmeticPlan(planId, procedureName) {
  if (!confirm(`Deletar o planejamento "${procedureName}"?\n\nEsta ação não pode ser desfeita.`)) {
    return;
  }

  try {
    const response = await fetch(`/api/crm/plans/${planId}`, {
      method: 'DELETE',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }
    });

    if (!response.ok) {
      const err = await response.json();
      showAlert(err.error || 'Erro ao deletar planejamento', 'danger');
      return;
    }

    // Recarregar dados
    await loadExistingPlans();
    renderCosmeticConduct();
    showAlert(`Planejamento "${procedureName}" deletado com sucesso`, 'success');
  } catch (error) {
    console.error('Erro ao deletar planejamento:', error);
    showAlert('Erro ao deletar planejamento', 'danger');
  }
}

window.toggleProcedurePerformed = async function (index) {
  const proc = cosmeticPlans[index];
  if (!proc || !proc.id) return;
  await promptCreateExecution(proc.id);
};

function generateBudget() {
  const patientId = getPatientId();

  if (cosmeticPlans.length === 0) {
    showAlert("Adicione procedimentos ao planejamento antes de gerar o orçamento", "warning");
    return;
  }

  fetch(`/api/prontuario/${patientId}/generate-budget`, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({ procedures: cosmeticPlans })
  })
    .then((response) => response.blob())
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `orcamento_${patientId}_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showAlert("Orçamento PDF gerado com sucesso!");
    })
    .catch((error) => {
      console.error(error);
      showAlert("Erro ao gerar orçamento.", "danger");
    });
}

function highlightConsultationGroup(consultationKey) {
  const btn = document.querySelector(`.accordion-button[data-consultation-key="${consultationKey}"]`);
  if (!btn) return;

  const badge = btn.querySelector(".badge.bg-primary");
  const categoryText = badge ? badge.textContent.trim().toLowerCase() : "";

  let category = "patologia";
  if (categoryText.includes("cosmiatria")) {
    category = "cosmiatria";
  } else if (categoryText.includes("transplante")) {
    category = "transplante_capilar";
  }

  renderHistoricalConsultationRightPanel(consultationKey, category);

  setTimeout(() => {
    const groupElement = document.getElementById(`group-${consultationKey}`);
    if (!groupElement) return;

    document.querySelectorAll(".consultation-group-header").forEach((el) => {
      el.classList.remove("highlighted-group");
    });

    groupElement.classList.add("highlighted-group");
    groupElement.scrollIntoView({ behavior: "smooth", block: "center" });

    setTimeout(() => {
      groupElement.classList.remove("highlighted-group");
    }, 3000);
  }, 300);
}

/* =========================
   TRANSPLANTE CAPILAR
========================= */

function toggleTransplantLocation() {
  const previousYes = document.getElementById("previousYes");
  const locationSection = document.getElementById("transplantLocationSection");

  if (!locationSection) return;
  locationSection.style.display = previousYes && previousYes.checked ? "" : "none";
}

function selectNorwood(classification) {
  document.querySelectorAll(".norwood-card").forEach((card) => {
    card.classList.remove("selected");
  });

  const wrapper = document.querySelector(`[data-norwood="${classification}"]`);
  const card = wrapper?.querySelector(".norwood-card");
  const radio = wrapper?.querySelector('input[name="norwood"]');

  if (card) card.classList.add("selected");
  if (radio) radio.checked = true;

  selectedNorwood = classification;
  if (currentCategory === "transplante_capilar") {
    renderTransplantRightPanelFromScreen();
  }
}

async function saveTransplantIndication() {
  const patientId = getPatientId();
  const indication = document.querySelector('input[name="transplantIndication"]:checked')?.value;
  if (!indication) return;

  try {
    const result = await core.fetchJson(`/api/patient/${patientId}/transplant-indication`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({ has_indication: indication === "sim" })
    });

    if (result.success) {
      showAlert("Indicação salva!", "success");
    } else {
      showAlert(result.error || "Erro ao salvar", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao salvar", "danger");
  }
}

/* =========================
   RECEITAS / DERMASCRIBE
========================= */

function abrirDermaScribe() {
  let patientName = cfg().patientName || "";

  if (!patientName) {
    const h2Element = document.querySelector("h2");
    if (h2Element) {
      patientName = h2Element.textContent.replace("Prontuário:", "").trim();
    }
  }

  const cleanName = patientName
    .replace(/\s*\(\d+\s*anos?\)/gi, "")
    .replace(/Editar\s*Cadastro/gi, "")
    .trim();

  const encodedName = encodeURIComponent(cleanName);
  const patientId = getPatientId();
  const dermaScribeUrl = `/dermascribe/?patient=${encodedName}&patient_id=${patientId}`;

  window.dermaScribeWindow = window.open(
    dermaScribeUrl,
    "DermaScribe",
    "width=1200,height=900,scrollbars=yes,resizable=yes"
  );
}

async function loadPrescriptionHistory() {
  const patientId = getPatientId();
  if (!patientId) return;

  try {
    const data = await core.fetchJson(`/dermascribe/api/patient/${patientId}/prescriptions`);
    const container = document.getElementById("prescriptionHistoryList");
    if (!container) return;

    if (!data.prescriptions || data.prescriptions.length === 0) {
      container.innerHTML = '<small class="text-muted">Nenhuma receita emitida</small>';
      return;
    }

    let html = '<ul class="list-unstyled mb-0">';
    data.prescriptions.forEach((p) => {
      let summary = "";
      if (p.oral && p.oral.length > 0) {
        summary += `Oral: ${p.oral.map((m) => m.medication || m).join(", ")}. `;
      }
      if (p.topical && p.topical.length > 0) {
        summary += `Tópico: ${p.topical.map((m) => m.medication || m).join(", ")}`;
      }

      html += `
        <li class="mb-2 p-2 bg-light rounded">
          <small class="text-muted">${core.escapeHtml(p.created_at)} - Dr(a). ${core.escapeHtml(p.doctor)}</small>
          <div class="small">${core.escapeHtml(summary || "Receita")}</div>
          <button class="btn btn-sm btn-outline-primary mt-1" onclick="printPrescription(${p.id})">
            <i class="bi bi-printer"></i> Imprimir
          </button>
        </li>
      `;
    });
    html += "</ul>";
    container.innerHTML = html;
  } catch (err) {
    console.error("Erro ao carregar histórico:", err);
  }
}

function printPrescription(prescriptionId) {
  window.open(`/dermascribe/prescription/${prescriptionId}/print`, "_blank");
}

function savePrescriptionToConduta(prescriptionData) {
  const patientId = getPatientId();
  if (!patientId) return;

  fetch(`/api/patient/${patientId}/prescription`, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify(prescriptionData)
  })
    .then((r) => r.json())
    .then((result) => {
      if (result.success) {
        showAlert("Receita salva na conduta!", "success");
        loadPrescriptionHistory();

        const condutaText = document.getElementById("condutaText");
        if (condutaText && prescriptionData.summary) {
          const separator = condutaText.value ? "\n\n" : "";
          condutaText.value = `${condutaText.value}${separator}📋 RECEITA: ${prescriptionData.summary}`;
        }
      } else {
        showAlert(result.error || "Erro ao salvar receita", "danger");
      }
    })
    .catch((err) => {
      console.error("Erro ao salvar receita:", err);
      showAlert("Erro ao salvar receita", "danger");
    });
}

/* =========================
   FINALIZAÇÃO
========================= */

function buildSurgicalPlanningPayload() {
  return {
    norwood: document.querySelector('input[name="norwood"]:checked')?.value || selectedNorwood || null,
    previous_transplant: document.querySelector('input[name="previousTransplant"]:checked')?.value || "nao",
    transplant_location: document.querySelector('input[name="transplantLocation"]:checked')?.value || null,
    case_type: document.querySelector('input[name="caseType"]:checked')?.value || "primaria",
    body_hair_needed: document.getElementById("bodyHair")?.checked || false,
    eyebrow_transplant: document.getElementById("eyebrowTransplant")?.checked || false,
    beard_transplant: document.getElementById("beardTransplant")?.checked || false,
    feminine_hair_transplant: document.getElementById("feminineHairTransplant")?.checked || false,
    frontal: document.getElementById("frontalTransplant")?.checked || false,
    crown: document.getElementById("crownTransplant")?.checked || false,
    complete: document.getElementById("completeTransplant")?.checked || false,
    complete_body_hair: document.getElementById("completeBodyHair")?.checked || false,
    dense_packing: document.getElementById("densePacking")?.checked || false,
    surgical_planning_text: document.getElementById("surgicalPlanning")?.value || "",
    clinical_conduct: document.getElementById("condutaText")?.value || ""
  };
}

function buildFinalizePayload() {
  const payload = {
    consultation_started: true,
    category: currentCategory,
    duration: getConsultationDuration(),
    queixa: document.getElementById("queixaText")?.value || "",
    anamnese: document.getElementById("anamneseText")?.value || "",
    diagnostico: document.getElementById("diagnosticoText")?.value || "",
    conduta: document.getElementById("condutaText")?.value || "",
    indicated_procedures: Array.from(document.querySelectorAll(".indicated-proc:checked")).map((cb) => parseInt(cb.value, 10)),
    performed_procedures: Array.from(document.querySelectorAll(".performed-proc:checked")).map((cb) => parseInt(cb.value, 10)),
    consultation_type: document.getElementById("editPatientType")?.value || "Particular"
  };

  const appointmentId = getAppointmentId();
  if (appointmentId !== null && appointmentId !== undefined) {
    payload.appointment_id = appointmentId;
  }

  const transplantIndication = document.querySelector('input[name="transplantIndication"]:checked');
  if (transplantIndication) {
    payload.transplant_indication = transplantIndication.value;
  }

  if (currentCategory === "transplante_capilar") {
    const planning = buildSurgicalPlanningPayload();
    payload.surgical_planning = planning;
    payload.transplant_data = planning;
  }

  if (currentCategory === "cosmiatria" && cosmeticPlans.length > 0) {
    payload.cosmetic_procedures = cosmeticPlans;

    const performedProcedures = cosmeticPlans.filter((p) => getPlanPerformed(p));
    const totalPerformed = performedProcedures.reduce((sum, p) => sum + getPlanRealizedValue(p), 0);

    if (totalPerformed > 0) {
      payload.checkout_amount = totalPerformed;
      payload.checkout_procedures = performedProcedures.map((p) => ({
        name: p.name,
        value: getPlanRealizedValue(p),
        budget: parseFloat(p.budget ?? p.value) || 0
      }));
    }
  }

  return payload;
}

async function finalizeConsultationUnified() {
  const patientId = getPatientId();
  if (!patientId) {
    showAlert("Paciente não encontrado.", "danger");
    return;
  }

  if (window.__finalizing) return;

  if (!confirm("Deseja finalizar o atendimento? Todos os dados serão salvos.")) {
    return;
  }

  window.__finalizing = true;

  const payload = buildFinalizePayload();
  const btn = document.querySelector('[data-action="finalizar-atendimento"]');
  const originalText = btn ? btn.innerHTML : "";

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Finalizando...';
  }

  try {
    const result = await core.fetchJson(`/api/prontuario/${patientId}/finalizar`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify(payload)
    });

    if (result.success) {
      if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
      }
      timerStartTime = null;
      alert("Atendimento finalizado com sucesso!");
      window.location.href = "/agenda";
    } else {
      showAlert(result.error || "Erro ao finalizar atendimento", "danger");
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  } catch (error) {
    console.error("[FINALIZAR] Erro:", error);
    alert(`Erro ao finalizar atendimento: ${error.message}`);
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  } finally {
    window.__finalizing = false;
  }
}

function finishConsultation() {
  finalizeConsultationUnified();
}

function finalizarAtendimento() {
  finalizeConsultationUnified();
}

/* =========================
   CONSULTAS / EDIÇÃO
========================= */

async function editConsultationDate(consultationId, dateTime) {
  document.getElementById("editConsultationId").value = consultationId;
  document.getElementById("editConsultationDateTime").value = dateTime;

  try {
    const notes = await core.fetchJson(`/api/appointments/${consultationId}/notes`);
    document.getElementById("editQueixa").value = notes.queixa?.content || "";
    document.getElementById("editQueixaId").value = notes.queixa?.id || "";

    document.getElementById("editAnamnese").value = notes.anamnese?.content || "";
    document.getElementById("editAnamneseId").value = notes.anamnese?.id || "";

    document.getElementById("editDiagnostico").value = notes.diagnostico?.content || "";
    document.getElementById("editDiagnosticoId").value = notes.diagnostico?.id || "";

    document.getElementById("editConduta").value = notes.conduta?.content || "";
    document.getElementById("editCondutaId").value = notes.conduta?.id || "";
  } catch (err) {
    console.error("Erro ao carregar notas:", err);
  }

  new bootstrap.Modal(document.getElementById("editConsultationModal")).show();
}

async function saveConsultationEdit() {
  const consultationId = document.getElementById("editConsultationId").value;
  const dateTime = document.getElementById("editConsultationDateTime").value;

  if (!dateTime) {
    showAlert("Por favor, selecione uma data e hora", "warning");
    return;
  }

  const updatePromises = [];
  const start = new Date(dateTime);
  const end = new Date(start.getTime() + 60 * 60 * 1000);

  updatePromises.push(
    core.fetchJson(`/api/appointments/${consultationId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({
        start: dateTime,
        end: end.toISOString().slice(0, 16).replace("T", " ")
      })
    })
  );

  const fields = ["Queixa", "Anamnese", "Diagnostico", "Conduta"];
  fields.forEach((field) => {
    const noteId = document.getElementById(`edit${field}Id`).value;
    const content = document.getElementById(`edit${field}`).value;

    if (noteId) {
      updatePromises.push(
        core.fetchJson(`/api/notes/${noteId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
          },
          body: JSON.stringify({ content })
        })
      );
    }
  });

  try {
    const results = await Promise.all(updatePromises);
    if (results.every((r) => r.success !== false)) {
      showAlert("Consulta atualizada com sucesso!", "success");
      bootstrap.Modal.getInstance(document.getElementById("editConsultationModal"))?.hide();
      setTimeout(() => window.location.reload(), 900);
    } else {
      showAlert("Erro ao atualizar algumas informações", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao atualizar consulta", "danger");
  }
}

async function deleteConsultation(consultationId, dateStr) {
  if (!confirm(`Tem certeza que deseja deletar a consulta de ${dateStr}?\n\nEsta ação não pode ser desfeita.`)) {
    return;
  }

  try {
    const result = await core.fetchJson(`/api/appointments/${consultationId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      }
    });

    if (result.success) {
      showAlert("Consulta deletada com sucesso!", "success");
      setTimeout(() => window.location.reload(), 900);
    } else {
      showAlert(result.error || "Erro ao deletar", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao deletar consulta", "danger");
  }
}

async function saveConsultationDate() {
  const input = document.getElementById("consultationDateInput");
  const status = document.getElementById("consultationDateStatus");
  const apptId = getAppointmentId();

  if (!apptId) {
    status.innerHTML = '<span class="text-danger"><i class="bi bi-exclamation-circle me-1"></i>Nenhum agendamento ativo encontrado.</span>';
    return;
  }

  if (!input?.value) {
    status.innerHTML = '<span class="text-warning"><i class="bi bi-exclamation-triangle me-1"></i>Selecione uma data.</span>';
    return;
  }

  status.innerHTML = '<span class="text-muted"><i class="bi bi-hourglass-split me-1"></i>Salvando...</span>';

  const isoDate = new Date(input.value).toISOString();

  try {
    const data = await core.fetchJson(`/api/appointments/${apptId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({ consultation_date: isoDate })
    });

    if (data.success !== false) {
      window.appointmentStartIso = input.value;
      status.innerHTML = '<span class="text-success"><i class="bi bi-check-circle me-1"></i>Data salva com sucesso!</span>';
      setTimeout(() => {
        status.innerHTML = "";
      }, 3000);
    } else {
      status.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle me-1"></i>${core.escapeHtml(data.error || "Erro ao salvar.")}</span>`;
    }
  } catch (err) {
    console.error(err);
    status.innerHTML = '<span class="text-danger"><i class="bi bi-x-circle me-1"></i>Erro de comunicação com o servidor.</span>';
  }
}

/* =========================
   EVOLUÇÕES
========================= */

function isSurgeryContext() {
  const modal = document.getElementById("evolutionModal");
  const ctx = modal?.dataset?.context;
  if (ctx === "surgery") return true;
  if (ctx === "consultation") return false;

  const sel = document.getElementById("evolutionConsultation");
  const selText = sel?.options?.[sel.selectedIndex]?.textContent?.toLowerCase?.() || "";
  if (selText.includes("cirurgia")) return true;

  const disp = document.getElementById("evolutionConsultationName");
  const dispText = disp?.textContent?.toLowerCase?.() || "";
  return dispText.includes("cirurgia");
}

function showHideSurgicalBox() {
  const box = document.getElementById("surgicalEvolutionFindings");
  if (!box) return;

  if (isSurgeryContext()) {
    box.style.display = "block";
  } else {
    box.style.display = "none";
    document.querySelectorAll(".surg-find").forEach((cb) => {
      cb.checked = false;
    });
  }
}

function getCheckedFindings() {
  return Array.from(document.querySelectorAll(".surg-find:checked")).map((x) => x.value);
}

function findingsToHuman(findings) {
  const map = {
    necrose: "Necrose",
    crostas: "Crostas",
    infeccao_secundaria: "Infecção secundária",
    foliculite_aguda: "Foliculite aguda",
    foliculite_cronica: "Foliculite crônica",
    rarefacao_capilar: "Rarefação capilar",
    falha_localizada: "Falha localizada"
  };
  return findings.map((f) => map[f] || f);
}

function injectFindingsIntoContentIfNeeded() {
  if (!isSurgeryContext()) return;

  const txt = document.getElementById("evolutionContent");
  if (!txt) return;

  const findings = getCheckedFindings();
  const human = findings.length ? findingsToHuman(findings).join(", ") : "Sem achados selecionados";

  const blockHeader = "[ACHADOS CIRÚRGICOS - CHECKLIST]";
  const block = `${blockHeader}\n- ${human}\n[/ACHADOS CIRÚRGICOS]\n`;

  const current = txt.value || "";
  const cleaned = current
    .replace(/\[ACHADOS CIRÚRGICOS - CHECKLIST\][\s\S]*?\[\/ACHADOS CIRÚRGICOS\]\n?/g, "")
    .trim();

  txt.value = `${block}\n${cleaned}`.trim();
}

async function loadConsultationsDropdown() {
  const patientId = getPatientId();

  try {
    const data = await core.fetchJson(`/api/patient/${patientId}/consultations`);
    const select = document.getElementById("evolutionConsultation");
    if (!select) return;

    select.innerHTML = '<option value="">-- Selecione uma consulta --</option>';

    (data.consultations || []).forEach((consultation) => {
      const option = document.createElement("option");
      option.value = consultation.id;
      option.textContent = `${consultation.date} - ${consultation.category || "Consulta"}`;
      select.appendChild(option);
    });
  } catch (err) {
    console.error("Erro ao carregar consultas:", err);
  }
}

function openEvolutionModal() {
  const modal = document.getElementById("evolutionModal");
  const now = new Date();

  document.getElementById("evolutionDate").value = now.toISOString().slice(0, 16);
  document.getElementById("evolutionContent").value = "";
  document.getElementById("evolutionConsultation").value = "";

  document.getElementById("evolutionConsultation").style.display = "block";
  document.getElementById("evolutionConsultationDisplay").style.display = "none";

  modal.dataset.fromConsultation = "false";
  modal.dataset.type = "consultation";
  modal.dataset.context = "consultation";
  delete modal.dataset.surgeryId;
  delete modal.dataset.consultationId;

  loadConsultationsDropdown();
  showHideSurgicalBox();
  new bootstrap.Modal(modal).show();
}

function openSurgeryEvolutionModal(surgeryId, surgeryDate) {
  const modal = document.getElementById("evolutionModal");

  document.getElementById("evolutionDate").value = new Date().toISOString().slice(0, 16);
  document.getElementById("evolutionContent").value = "";
  document.getElementById("evolutionConsultation").style.display = "none";
  document.getElementById("evolutionConsultationDisplay").style.display = "block";
  document.getElementById("evolutionConsultationName").textContent = `🏥 Cirurgia de ${surgeryDate}`;

  modal.dataset.surgeryId = surgeryId;
  modal.dataset.fromConsultation = "false";
  modal.dataset.type = "surgery";
  modal.dataset.context = "surgery";

  showHideSurgicalBox();
  new bootstrap.Modal(modal).show();
}

function openEvolutionFromConsultation(consultationId, consultationDate) {
  const modal = document.getElementById("evolutionModal");
  const now = new Date();

  document.getElementById("evolutionDate").value = now.toISOString().slice(0, 16);
  document.getElementById("evolutionContent").value = "";
  document.getElementById("evolutionConsultation").style.display = "none";
  document.getElementById("evolutionConsultationDisplay").style.display = "block";
  document.getElementById("evolutionConsultationName").textContent = `Consulta de ${consultationDate}`;

  modal.dataset.consultationId = consultationId;
  modal.dataset.type = "consultation";
  modal.dataset.context = "consultation";
  delete modal.dataset.surgeryId;

  showHideSurgicalBox();
  new bootstrap.Modal(modal).show();
}

async function saveEvolution() {
  if (!ensureClinicalEditAllowed()) return;
  const modal = document.getElementById("evolutionModal");
  const contentEl = document.getElementById("evolutionContent");
  const date = document.getElementById("evolutionDate").value;
  const surgeryId = modal.dataset.surgeryId;
  const type = modal.dataset.type;
  const patientId = getPatientId();

  injectFindingsIntoContentIfNeeded();

  const content = contentEl.value.trim();
  if (!content) {
    showAlert("Descrição vazia!", "warning");
    return;
  }

  try {
    if (type === "surgery" && surgeryId) {
      const result = await core.fetchJson(`/api/patient/${patientId}/surgery/${surgeryId}/evolution`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ content, evolution_date: date })
      });

      if (result.success) {
        showAlert("✅ Evolução de cirurgia salva!", "success");
        bootstrap.Modal.getInstance(modal)?.hide();
        loadTimeline();
      } else {
        showAlert(result.error || "Erro ao salvar", "danger");
      }
      return;
    }

    let consultationId = modal.dataset.consultationId || document.getElementById("evolutionConsultation").value;
    if (!consultationId) {
      showAlert("Selecione uma consulta!", "warning");
      return;
    }

    consultationId = parseInt(String(consultationId).trim(), 10);
    if (isNaN(consultationId)) {
      showAlert("ID de consulta inválido!", "warning");
      return;
    }

    const result = await core.fetchJson(`/api/patient/${patientId}/evolution`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({
        content,
        evolution_date: date,
        consultation_id: consultationId
      })
    });

    if (result.success) {
      showAlert("Evolução salva com sucesso!", "success");
      bootstrap.Modal.getInstance(modal)?.hide();
      loadTimeline();
    } else {
      showAlert(result.error || "Erro ao salvar", "danger");
    }
  } catch (err) {
    console.error("Erro ao salvar evolução:", err);
    showAlert(`Erro ao salvar evolução: ${err.message}`, "danger");
  }
}

async function saveQuickEvolution(consultationId) {
  if (!ensureClinicalEditAllowed()) return;
  const patientId = getPatientId();
  const textarea = document.getElementById(`newEvoText${consultationId}`);
  const content = textarea?.value.trim() || "";

  if (!content) {
    showAlert("Por favor, digite o conteúdo da evolução.", "warning");
    return;
  }

  try {
    const result = await core.fetchJson(`/api/patient/${patientId}/evolution`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({
        content,
        consultation_id: consultationId,
        evolution_date: new Date().toISOString()
      })
    });

    if (result.success) {
      showAlert("Evolução salva com sucesso!", "success");
      loadTimeline();
    } else {
      showAlert(result.error || "Erro ao salvar", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao salvar evolução", "danger");
  }
}

async function deleteEvolution(evoId) {
  if (!ensureClinicalEditAllowed()) return;
  if (!confirm("Tem certeza que deseja deletar esta evolução?")) return;

  try {
    const result = await core.fetchJson(`/api/evolution/${evoId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      }
    });

    if (result.success) {
      showAlert("Evolução deletada!", "success");
      loadTimeline();
    } else {
      showAlert(result.error || "Erro ao deletar", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao deletar evolução", "danger");
  }
}

async function deleteSurgeryEvolution(evolutionId) {
  if (!confirm("Tem certeza que deseja deletar esta evolução da cirurgia?")) return;

  try {
    const result = await core.fetchJson(`/api/patient/surgery-evolution/${evolutionId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      }
    });

    if (result.success) {
      showAlert("✅ Evolução deletada!", "success");
      loadTimeline();
    } else {
      showAlert(result.error || "Erro ao deletar", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Erro ao deletar evolução", "danger");
  }
}

function renderEvolutionsInAccordion(consultations = []) {
  setTimeout(() => {
    consultations.forEach((consultation) => {
      const container = document.getElementById(`evolutionsContainer${consultation.id}`);
      if (!container) return;

      container.innerHTML = "";

      if (canEditClinical()) {
        const quickEvoDiv = document.createElement("div");
        quickEvoDiv.className = "mt-3 p-3 bg-light rounded border mb-3";
        quickEvoDiv.innerHTML = `
          <h6 class="text-muted mb-2"><i class="bi bi-plus-circle"></i> Nova Evolução</h6>
          <textarea class="form-control mb-2" rows="3" id="newEvoText${consultation.id}" placeholder="Descreva a evolução do paciente..." style="background-color: #fff;"></textarea>
          <div class="d-flex justify-content-between">
            <button class="btn btn-sm btn-success" onclick="saveQuickEvolution(${consultation.id})">
              <i class="bi bi-save"></i> Salvar Evolução
            </button>
            <button class="btn btn-sm btn-outline-secondary" onclick="openEvolutionFromConsultation(${consultation.id}, '${consultation.date || ""}')">
              <i class="bi bi-arrows-fullscreen"></i> Tela Cheia
            </button>
          </div>
        `;
        container.appendChild(quickEvoDiv);
      }

      if (consultation.evolutions && consultation.evolutions.length > 0) {
        const historyTitle = document.createElement("div");
        historyTitle.className = "border-top pt-2 mt-2 mb-2";
        historyTitle.innerHTML = '<small class="text-muted fw-bold">Evoluções Anteriores:</small>';
        container.appendChild(historyTitle);

        consultation.evolutions.forEach((evo) => {
          const evoDiv = document.createElement("div");
          evoDiv.className = "mb-2 p-2 bg-white rounded border-start border-4 border-success shadow-sm";
          evoDiv.innerHTML = `
            <div class="d-flex justify-content-between">
              <small class="text-muted fw-bold">${core.escapeHtml(evo.date)} - Dr. ${core.escapeHtml(evo.doctor)}</small>
              ${canEditClinical() ? `<button class="btn btn-link btn-sm p-0 text-danger" onclick="deleteEvolution(${evo.id})"><i class="bi bi-trash"></i></button>` : ''}
            </div>
            <div class="mt-1" style="white-space: pre-wrap;">${core.escapeHtml(evo.content)}</div>
          `;
          container.appendChild(evoDiv);
        });
      }
    });
  }, 350);
}

/* =========================
   HISTÓRICO DE CIRURGIAS
========================= */

function calculateDaysPassed(dateStr) {
  if (!dateStr) return "";
  let surgeryDate;

  if (dateStr.includes("/")) {
    const [day, month, year] = dateStr.split("/").map(Number);
    surgeryDate = new Date(year, month - 1, day);
  } else {
    surgeryDate = new Date(dateStr);
  }

  const today = new Date();
  const diffTime = today - surgeryDate;
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  const years = Math.floor(diffDays / 365);
  const months = Math.floor((diffDays % 365) / 30);
  const days = diffDays % 30;

  const parts = [];
  if (years > 0) parts.push(`${years} ano${years !== 1 ? "s" : ""}`);
  if (months > 0) parts.push(`${months} mês${months !== 1 ? "es" : ""}`);
  if (days > 0 || parts.length === 0) parts.push(`${days} dia${days !== 1 ? "s" : ""}`);

  return parts.slice(0, 2).join(" e ");
}

function groupSurgeriesByMonthYear(surgeries) {
  const grouped = {};

  surgeries.forEach((surgery) => {
    const raw = surgery.surgery_date || "";
    let day, month, year;

    if (raw.includes("/")) {
      [day, month, year] = raw.split("/");
    } else {
      const d = new Date(raw);
      day = String(d.getDate()).padStart(2, "0");
      month = String(d.getMonth() + 1).padStart(2, "0");
      year = String(d.getFullYear());
    }

    const key = `${month}/${year}`;
    const monthYear = new Date(Number(year), Number(month) - 1).toLocaleDateString("pt-BR", {
      month: "long",
      year: "numeric"
    });

    if (!grouped[key]) grouped[key] = { monthYear, surgeries: [] };
    grouped[key].surgeries.push(surgery);
  });

  return grouped;
}

function renderSurgeryHistoryCard(surgeries = []) {
  const container = document.getElementById("surgeriesContainer");
  if (!container) return;

  container.innerHTML = "";

  if (surgeries.length === 0) {
    container.innerHTML = '<p class="text-muted text-center">Nenhuma cirurgia registrada.</p>';
    return;
  }

  const grouped = groupSurgeriesByMonthYear(surgeries);

  Object.keys(grouped)
    .sort()
    .reverse()
    .forEach((key) => {
      const group = grouped[key];

      const groupHeader = document.createElement("div");
      groupHeader.className = "mb-3 mt-3 pt-2 border-top";
      groupHeader.innerHTML = `<h6 class="text-secondary text-capitalize">${core.escapeHtml(group.monthYear)}</h6>`;
      container.appendChild(groupHeader);

      group.surgeries.forEach((surgery) => {
        const daysPassed = calculateDaysPassed(surgery.surgery_date);

        const surgeryDiv = document.createElement("div");
        surgeryDiv.className = "mb-4 p-3 border rounded";
        surgeryDiv.style.backgroundColor = "#e3f2fd";
        surgeryDiv.style.borderLeft = "5px solid #2196F3";

        surgeryDiv.innerHTML = `
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div>
              <h6 class="mb-1"><i class="bi bi-heart-pulse"></i> <strong>${core.escapeHtml(surgery.surgery_date)}</strong></h6>
              <p class="mb-1"><small class="text-success"><i class="bi bi-hourglass-split"></i> ${core.escapeHtml(daysPassed)}</small></p>
              <p class="mb-1"><small><strong>Cirurgia de Transplante</strong></small></p>
            </div>
            <button class="btn btn-sm btn-outline-success" onclick="createEvolutionForSurgery(${surgery.id}, '${core.escapeHtml(surgery.surgery_date_iso || surgery.surgery_date)}')">
              <i class="bi bi-plus"></i> Evolução
            </button>
          </div>
          <p style="white-space: pre-wrap;"><strong>Dados:</strong> ${core.escapeHtml(surgery.surgical_data || "")}</p>
          ${surgery.observations ? `<p><strong>Observações:</strong> ${core.escapeHtml(surgery.observations)}</p>` : ""}
          <p class="mb-3"><small class="text-muted">Dr. ${core.escapeHtml(surgery.doctor_name || "")}</small></p>
        `;

        const evolutionsDiv = document.createElement("div");
        evolutionsDiv.className = "mt-3 pt-3 border-top";

        const evoHeader = document.createElement("h6");
        evoHeader.className = "text-success mb-2";
        evoHeader.innerHTML = '<i class="bi bi-stickies"></i> Evoluções';
        evolutionsDiv.appendChild(evoHeader);

        if (surgery.evolutions && surgery.evolutions.length > 0) {
          const evosContainer = document.createElement("div");
          evosContainer.className = "ms-2 ps-3 border-start border-success";

          surgery.evolutions.forEach((evo) => {
            const evoDiv = document.createElement("div");
            evoDiv.className = "mb-3 p-2 bg-light rounded";
            evoDiv.style.borderLeft = "4px solid #198754";
            evoDiv.innerHTML = `
              <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                  <p class="mb-1 mt-2" style="white-space: pre-wrap;">${core.escapeHtml(evo.content)}</p>
                  <small class="text-muted">Dr. ${core.escapeHtml(evo.doctor)}</small>
                </div>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteSurgeryEvolution(${evo.id})">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            `;
            evosContainer.appendChild(evoDiv);
          });

          evolutionsDiv.appendChild(evosContainer);
        } else {
          const noEvo = document.createElement("p");
          noEvo.className = "text-muted small mb-0";
          noEvo.innerHTML = "<em>Nenhuma evolução registrada</em>";
          evolutionsDiv.appendChild(noEvo);
        }

        surgeryDiv.appendChild(evolutionsDiv);
        container.appendChild(surgeryDiv);
      });
    });
}

/* =========================
   TIMELINE LOAD
========================= */

function renderTimeline(consultations = [], surgeries = []) {
  window.timelineConsultations = consultations || [];
  window.timelineSurgeries = surgeries || [];
  renderEvolutionsInAccordion(consultations || []);
  renderSurgeryHistoryCard(surgeries || []);
}

async function loadTimeline() {
  const patientId = getPatientId();
  if (!patientId) return;

  try {
    const [consultations, surgeries] = await Promise.all([
      core.fetchJson(`/api/patient/${patientId}/evolutions`),
      core.fetchJson(`/api/patient/${patientId}/surgeries`)
    ]);

    renderTimeline(consultations || [], surgeries || []);
  } catch (err) {
    console.error("Erro ao carregar timeline:", err);
  }
}

/* =========================
   CIRURGIA AGENDAMENTO
========================= */

async function scheduleTransplantSurgery(button) {
  const patientId = button.getAttribute("data-patient-id") || getPatientId();
  if (!patientId) {
    alert("Erro crítico: ID do paciente não localizado.");
    return;
  }

  const date = await openSurgeryScheduleDatePicker();
  if (!date) return;

  const rightCardSnapshot = getFixedRightCardSnapshot();

  button.disabled = true;
  const originalText = button.innerHTML;
  button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processando...';

  try {
    const out = await core.fetchJson(`/api/patient/${patientId}/transplant/schedule-surgery`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({
        surgery_date: date,
        right_card_snapshot: rightCardSnapshot
      })
    });

    if (!out || !out.success) {
      alert(out?.error || "Erro ao processar agendamento.");
      return;
    }

    if (out.calendar_event_created === false) {
      alert(
        "Sucesso: Cirurgia agendada no sistema.\n\nAviso: Não foi possível criar o evento no Google Calendar automaticamente. Erro: " +
          (out.calendar_error || "desconhecido")
      );
    } else {
      alert("Sucesso: Cirurgia agendada e evento criado no Google Calendar!");
    }

    location.reload();
  } catch (err) {
    console.error("[SurgerySchedule] Exception:", err);
    alert("Erro inesperado ao conectar com o servidor.");
  } finally {
    button.disabled = false;
    button.innerHTML = originalText;
  }
}

function getFixedRightCardSnapshot() {
  const panel = document.getElementById("clinicalRightPanel") || document.getElementById("cosmeticRightColumn");
  if (!panel) return "Painel lateral não encontrado no momento do agendamento.";

  return panel.innerText
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function openSurgeryScheduleDatePicker() {
  return new Promise((resolve) => {
    const modalEl = document.getElementById("scheduleTransplantSurgeryModal");
    const dateInput = document.getElementById("scheduleTransplantSurgeryDate");
    const confirmBtn = document.getElementById("confirmScheduleTransplantSurgery");

    if (!modalEl || !dateInput || !confirmBtn || !window.bootstrap) {
      const fallback = prompt("Data da cirurgia (YYYY-MM-DD):", new Date().toISOString().split("T")[0]);
      resolve(fallback || null);
      return;
    }

    dateInput.value = new Date().toISOString().split("T")[0];
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

    let settled = false;
    const cleanup = () => {
      confirmBtn.removeEventListener("click", onConfirm);
      modalEl.removeEventListener("hidden.bs.modal", onHidden);
    };

    const onConfirm = () => {
      const selectedDate = dateInput.value;
      if (!selectedDate) {
        alert("Selecione uma data para a cirurgia.");
        return;
      }
      settled = true;
      cleanup();
      modal.hide();
      resolve(selectedDate);
    };

    const onHidden = () => {
      if (!settled) {
        cleanup();
        resolve(null);
      }
    };

    confirmBtn.addEventListener("click", onConfirm);
    modalEl.addEventListener("hidden.bs.modal", onHidden);
    modal.show();
  });
}

/* =========================
   RESUMO PLANEJAMENTO
========================= */

async function loadTransplantPlanningSummary() {
  const card = document.getElementById("transplantPlanningSummaryInEvolution");
  if (!card) return;

  const patientId = getPatientId();
  if (!patientId) return;

  try {
    const data = await core.fetchJson(`/api/patient/${patientId}/transplant/planning-summary`);
    if (!data || !data.success || !data.has_planning) return;

    const planningEl = document.getElementById("transplantPlanningTextInEvolution");
    const surgEl = document.getElementById("transplantLastSurgeryDateInEvolution");

    if (planningEl) planningEl.textContent = data.planning || "";
    if (surgEl) surgEl.textContent = data.last_surgery_date || "—";

    card.style.display = "";
  } catch (err) {
    console.warn("Falha ao carregar resumo do transplante:", err);
  }
}

function formatSurgicalPlanDisplays() {
  const labels = {
    norwood: "Escala Norwood",
    previous_transplant: "Transplante Anterior",
    transplant_location: "Local do Transplante",
    case_type: "Tipo de Caso",
    body_hair_needed: "Body Hair Transplant",
    eyebrow_transplant: "Transplante Sobrancelha",
    beard_transplant: "Transplante Barba",
    feminine_hair_transplant: "Transplante Capilar Feminino",
    frontal: "Frontal",
    crown: "Coroa",
    complete: "Completo",
    complete_body_hair: "Body Hair",
    dense_packing: "Dense Packing",
    surgical_planning_text: "Observações",
    clinical_conduct: "Conduta Clínica"
  };

  document.querySelectorAll(".js-surgical-plan-display").forEach((container) => {
    const raw = container.getAttribute("data-plan-json");
    if (!raw) return;

    try {
      const decoded = JSON.parse(raw);
      const planData = typeof decoded === "string" ? JSON.parse(decoded) : decoded;

      if (!planData || typeof planData !== "object") {
        container.innerHTML = `<p class="mb-0 small">${core.escapeHtml(String(decoded))}</p>`;
        return;
      }

      let html = '<dl class="row mb-0 small">';
      let hasContent = false;

      Object.entries(planData).forEach(([key, val]) => {
        if (val === null || val === false || val === "" || val === undefined) return;
        hasContent = true;

        const label = labels[key] || key;
        let display = val;
        if (typeof val === "boolean") {
          display = val ? "Sim" : "Não";
        } else if (typeof val === "string") {
          display = nl2br(core.escapeHtml(val));
        } else {
          display = escapeHtml(String(val));
        }

        html += `<dt class="col-sm-5 text-muted">${core.escapeHtml(label)}:</dt><dd class="col-sm-7"><strong>${display}</strong></dd>`;
      });

      html += "</dl>";

      if (!hasContent) {
        const wrapper = container.closest(".js-surgical-plan-wrapper");
        if (wrapper) wrapper.style.display = "none";
        return;
      }

      container.innerHTML = html;
    } catch (e) {
      console.error("Erro ao processar planejamento:", e);
      container.innerHTML = `<p class="mb-0 small">${core.escapeHtml(raw)}</p>`;
    }
  });
}

/* =========================
   WINDOW MESSAGE
========================= */

window.addEventListener("message", function (event) {
  if (event.data && event.data.type === "prescription_saved") {
    showAlert("Receita salva com sucesso no prontuário!", "success");
    loadPrescriptionHistory();

    const prescriptionData = event.data;
    const condutaText = document.getElementById("condutaText");
    if (condutaText) {
      let receitaTexto = "\n\n📋 RECEITA EMITIDA:\n";

      if (prescriptionData.oral && prescriptionData.oral.length > 0) {
        receitaTexto += "USO ORAL:\n";
        prescriptionData.oral.forEach((med, i) => {
          receitaTexto += `  ${i + 1}. ${med.medication} - ${med.instructions || ""}\n`;
        });
      }

      if (prescriptionData.topical && prescriptionData.topical.length > 0) {
        receitaTexto += "USO TÓPICO:\n";
        prescriptionData.topical.forEach((med, i) => {
          receitaTexto += `  ${i + 1}. ${med.medication} - ${med.instructions || ""}\n`;
        });
      }

      condutaText.value = `${condutaText.value}${receitaTexto}`;
    }
  }
});

/* =========================
   INIT
========================= */

document.addEventListener("click", function (e) {
  const dot = e.target.closest(".js-timeline-dot");
  if (dot) {
    e.preventDefault();
    e.stopPropagation();
    handleTimelineDotClick(dot);
    return;
  }

  const toggleProcBtn = e.target.closest(".btn-toggle-proc");
  if (toggleProcBtn) {
    e.preventDefault();
    e.stopPropagation();
    const idx = parseInt(toggleProcBtn.getAttribute("data-index"), 10);
    window.toggleProcedurePerformed(idx);
    return;
  }

  const scheduleBtn = e.target.closest(".js-schedule-transplant-surgery");
  if (scheduleBtn) {
    e.preventDefault();
    e.stopPropagation();
    scheduleTransplantSurgery(scheduleBtn);
    return;
  }

  if (!e.target.closest(".timeline-dot-wrapper")) {
    closeAllTimelinePopovers();
  }
});

document.addEventListener("DOMContentLoaded", async function () {
  window.patientId = getPatientId();

  initSpeechRecognition();
  initCategoryFromCheckedRadio();

  const categoryInputs = document.querySelectorAll('input[name="category"]');
  categoryInputs.forEach((input) => {
    input.removeEventListener("change", handleCategoryChange);
    input.addEventListener("change", handleCategoryChange);
  });

  document.querySelectorAll(".accordion-button[data-consultation-key]").forEach((btn) => {
    btn.addEventListener("click", function () {
      const consultationKey = btn.getAttribute("data-consultation-key");
      if (!consultationKey) return;

      const badge = btn.querySelector(".badge.bg-primary");
      const historyCategory = resolveHistoryCategoryFromBadgeText(badge ? badge.textContent : "");

      renderHistoricalConsultationRightPanel(consultationKey, historyCategory);

      if (historyCategory === "cosmiatria" && currentCategory === "cosmiatria") {
        setCosmeticContextFromConsultation(consultationKey);
      }
    });
  });

  const sel = document.getElementById("evolutionConsultation");
  if (sel) {
    sel.addEventListener("change", function () {
      const modal = document.getElementById("evolutionModal");
      const txt = sel.options[sel.selectedIndex]?.textContent?.toLowerCase?.() || "";
      if (modal) modal.dataset.context = txt.includes("cirurgia") ? "surgery" : "consultation";
      showHideSurgicalBox();
    });
  }

  const evoModal = document.getElementById("evolutionModal");
  if (evoModal) {
    evoModal.addEventListener("shown.bs.modal", showHideSurgicalBox);
  }

  const attentionContent = document.getElementById("attentionContent");
  if (attentionContent && attentionContent.textContent.trim()) {
    setTimeout(() => {
      const attentionText = document.getElementById("attentionText");
      if (attentionText) attentionText.value = attentionContent.textContent;
    }, 300);
  }

  if (!getAppointmentId()) {
    try {
      const data = await core.fetchJson(`/api/patient/${getPatientId()}/today-appointment`);
      if (data.appointment_id) {
        window.appointmentId = data.appointment_id;
      }
    } catch (err) {
      console.log("No today appointment found");
    }
  }

  document.querySelectorAll('a[href="#data-consulta"]').forEach((tab) => {
    tab.addEventListener("shown.bs.tab", function () {
      const input = document.getElementById("consultationDateInput");
      if (!input) return;

      if (window.appointmentStartIso) {
        input.value = window.appointmentStartIso;
      } else {
        const now = new Date();
        now.setSeconds(0, 0);
        input.value = now.toISOString().slice(0, 16);
      }
    });
  });

  const transplantFields = [
    "surgicalPlanning",
    "condutaText",
    "bodyHair",
    "eyebrowTransplant",
    "beardTransplant",
    "feminineHairTransplant",
    "frontalTransplant",
    "crownTransplant",
    "completeTransplant",
    "completeBodyHair",
    "densePacking",
    "previousNo",
    "previousYes",
    "locationICB",
    "locationOther",
    "casePrimary",
    "caseSecondary"
  ];

  transplantFields.forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("input", () => {
      if (currentCategory === "transplante_capilar") renderTransplantRightPanelFromScreen();
    });
    el.addEventListener("change", () => {
      if (currentCategory === "transplante_capilar") renderTransplantRightPanelFromScreen();
    });
  });

  ["queixaText", "diagnosticoText", "condutaText"].forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("input", () => {
      if (currentCategory === "patologia") renderPatologiaRightPanelFromScreen();
      if (currentCategory === "transplante_capilar") renderTransplantRightPanelFromScreen();
    });
  });

  formatSurgicalPlanDisplays();
  loadPrescriptionHistory();
  loadTimeline();
  await loadExistingPlans();
  loadTransplantPlanningSummary();
  toggleTransplantLocation();
  updateCosmeticTotal();

  initializeRightPanelFromHistory();
  updateMainLayoutColumns(true);

  window.addEventListener("resize", () => updateMainLayoutColumns(true));

});

/* =========================
   EXPORTS GLOBAIS
========================= */

window.showAlert = showAlert;
window.getCSRFToken = getCSRFToken;

window.startDictation = startDictation;
window.stopDictation = stopDictation;
window.startConsultation = startConsultation;
window.finishConsultation = finishConsultation;
window.finalizarAtendimento = finalizarAtendimento;

window.updatePatientStars = updatePatientStars;
window.openAttentionModal = openAttentionModal;
window.saveAttentionNote = saveAttentionNote;
window.openEditPatientModal = openEditPatientModal;
window.savePatientData = savePatientData;
window.uploadPatientPhoto = uploadPatientPhoto;
window.deletePatientPhoto = deletePatientPhoto;
window.savePatientTags = savePatientTags;

window.scrollToConsultation = scrollToConsultation;
window.scrollToEvent = scrollToEvent;
window.recalculateEvolution = recalculateEvolution;

window.addCosmeticProcedure = addCosmeticProcedure;
window.editCosmeticProcedure = editCosmeticProcedure;
window.removeCosmeticProcedure = removeCosmeticProcedure;
window.updatePlanValue = updatePlanValue;
window.updatePlanStatus = updatePlanStatus;
window.togglePlanSessions = togglePlanSessions;
window.promptCreateExecution = promptCreateExecution;
window.promptEditExecution = promptEditExecution;
window.removeExecution = removeExecution;
window.performCosmeticProcedure = performCosmeticProcedure;
window.generateBudget = generateBudget;
window.highlightConsultationGroup = highlightConsultationGroup;
window.clearCosmeticContext = clearCosmeticContext;
window.renderRightPanel = renderRightPanel;

window.toggleTransplantLocation = toggleTransplantLocation;
window.selectNorwood = selectNorwood;
window.saveTransplantIndication = saveTransplantIndication;

window.abrirDermaScribe = abrirDermaScribe;
window.loadPrescriptionHistory = loadPrescriptionHistory;
window.printPrescription = printPrescription;
window.savePrescriptionToConduta = savePrescriptionToConduta;

window.editConsultationDate = editConsultationDate;
window.saveConsultationEdit = saveConsultationEdit;
window.deleteConsultation = deleteConsultation;
window.saveConsultationDate = saveConsultationDate;

window.openEvolutionModal = openEvolutionModal;
window.openEvolutionFromConsultation = openEvolutionFromConsultation;
function refreshSurgeryHistory() {
  if (typeof window.loadTimeline === "function") {
    window.loadTimeline();
  }
}

window.openSurgeryEvolutionModal = openSurgeryEvolutionModal;
window.saveEvolution = saveEvolution;
window.saveQuickEvolution = saveQuickEvolution;
window.deleteEvolution = deleteEvolution;
window.deleteSurgeryEvolution = deleteSurgeryEvolution;

window.loadTimeline = loadTimeline;
window.renderHistoricalConsultationRightPanel = renderHistoricalConsultationRightPanel;
window.renderPatologiaRightPanelFromScreen = renderPatologiaRightPanelFromScreen;
window.renderTransplantRightPanelFromScreen = renderTransplantRightPanelFromScreen;
window.showRightPanel = showRightPanel;
window.hideRightPanel = hideRightPanel;

window.refreshSurgeryHistory = function () {
  if (window.ProntuarioCore) {
    window.ProntuarioCore.refreshProntuarioScreen();
    return;
  }

  if (typeof window.loadTimeline === "function") {
    window.loadTimeline();
  }
};
