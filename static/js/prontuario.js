console.log('prontuario.js carregado v=20260306-1');
let timerInterval = null;
let timerStartTime = null;
let recognition = null;
let activeTextarea = null;

// ========== MENSAGENS CROSS-WINDOW ==========
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'prescription_saved') {
        showAlert('Receita salva com sucesso no prontuário!', 'success');
        if (typeof loadPrescriptionHistory === 'function') loadPrescriptionHistory();

        const prescriptionData = event.data;
        const condutaText = document.getElementById('condutaText');
        if (condutaText) {
            let receitaTexto = '\n\n📋 RECEITA EMITIDA:\n';
            if (prescriptionData.oral && prescriptionData.oral.length > 0) {
                receitaTexto += 'USO ORAL:\n';
                prescriptionData.oral.forEach((med, i) => {
                    receitaTexto += `  ${i+1}. ${med.medication} - ${med.instructions || ''}\n`;
                });
            }
            if (prescriptionData.topical && prescriptionData.topical.length > 0) {
                receitaTexto += 'USO TÓPICO:\n';
                prescriptionData.topical.forEach((med, i) => {
                    receitaTexto += `  ${i+1}. ${med.medication} - ${med.instructions || ''}\n`;
                });
            }
            condutaText.value = condutaText.value + receitaTexto;
        }
    }
});

// ========== RECONHECIMENTO DE VOZ ==========
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function(event) {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript + ' ';
            }
        }
        if (activeTextarea && finalTranscript) {
            activeTextarea.value += finalTranscript;
            activeTextarea.dispatchEvent(new Event('input'));
        }
    };

    recognition.onerror = function(event) {
        console.error('Erro no reconhecimento de voz:', event.error);
        stopDictation();
    };

    recognition.onend = function() {
        stopDictation();
    };
}

function startDictation(textareaId, event) {
    if (!recognition) {
        showAlert('Reconhecimento de voz não suportado neste navegador.', 'warning');
        return;
    }
    activeTextarea = document.getElementById(textareaId);
    const button = event.target.closest('button');
    if (button.classList.contains('dictation-active')) {
        stopDictation();
    } else {
        try {
            recognition.stop();
            setTimeout(() => recognition.start(), 100);
            button.classList.add('dictation-active');
            button.innerHTML = '<i class="bi bi-mic-fill"></i> Gravando...';
        } catch (error) {
            console.error('Erro ao iniciar ditado:', error);
        }
    }
}

function stopDictation() {
    if (recognition) recognition.stop();
    document.querySelectorAll('.dictation-active').forEach(button => {
        button.classList.remove('dictation-active');
        button.innerHTML = '<i class="bi bi-mic"></i> Ditado';
    });
    activeTextarea = null;
}

// ========== CRONÔMETRO ==========
function startConsultation() {
    const button = document.getElementById('startTimer');
    const display = document.getElementById('timerDisplay');
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        button.innerHTML = '<i class="bi bi-play-circle"></i> Iniciar Atendimento';
        button.classList.replace('btn-danger', 'btn-success');
        display.classList.remove('timer-running');
    } else {
        timerStartTime = Date.now();
        button.innerHTML = '<i class="bi bi-stop-circle"></i> Parar Atendimento';
        button.classList.replace('btn-success', 'btn-danger');
        display.classList.add('timer-running');
        timerInterval = setInterval(updateTimer, 1000);
        updateTimer();
    }
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - timerStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('timerDisplay').textContent =
        `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// ========== GESTÃO DE CATEGORIAS ==========
let currentCategory = 'patologia';
let cosmeticProcedures = [];
let editingCosmeticProcedureIndex = null;

function handleCategoryChange(event) {
    const newCategory = event.target.value;
    const sectionGeral = document.getElementById('section_geral');
    const sectionCosmiatria = document.getElementById('section_cosmiatria');
    const sectionTransplante = document.getElementById('section_transplante');
    const indicatedProcedures = document.getElementById('indicatedProceduresSection');
    const cosmeticConduct = document.getElementById('cosmeticConductSection');

    if (sectionGeral) sectionGeral.style.display = 'block';
    if (sectionCosmiatria) sectionCosmiatria.style.display = (newCategory === 'cosmiatria') ? 'block' : 'none';
    if (sectionTransplante) sectionTransplante.style.display = (newCategory === 'transplante_capilar') ? 'block' : 'none';
    if (indicatedProcedures) indicatedProcedures.style.display = (newCategory === 'patologia') ? 'block' : 'none';
    if (cosmeticConduct) cosmeticConduct.style.display = (newCategory === 'cosmiatria') ? 'block' : 'none';

    currentCategory = newCategory;
    if ((newCategory === 'cosmiatria' || newCategory === 'transplante_capilar') && !timerStartTime) {
        startConsultation();
    }
}

// ========== COSMIATRIA FUNCTIONS ==========
function renderCosmeticProcedures() {
    const tbody = document.getElementById('cosmeticPlanBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (cosmeticProcedures.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3 small">Nenhum procedimento planejado ainda</td></tr>';
        return;
    }
    cosmeticProcedures.forEach((proc, index) => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td class="ps-3">${proc.name}</td>
            <td>${proc.value.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
            <td>${proc.months} meses</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-primary border-0" onclick="editCosmeticProcedure(${index})"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-outline-danger border-0" onclick="removeCosmeticProcedure(${index})"><i class="bi bi-trash"></i></button>
            </td>
        `;
    });
}

function updateCosmeticTotal() {
    const total = cosmeticProcedures.reduce((sum, p) => sum + p.value, 0);
    const el = document.getElementById('cosmeticTotal');
    if (el) el.textContent = total.toLocaleString('pt-BR', {minimumFractionDigits: 2});
}

function addCosmeticProcedure() {
    const nameInput = document.getElementById('newProcedureName');
    const valueInput = document.getElementById('newProcedureValue');
    const monthsInput = document.getElementById('newProcedureMonths');
    const obsInput = document.getElementById('newProcedureObservations');

    const name = nameInput.value.trim();
    const value = parseFloat(valueInput.value) || 0;
    const months = parseInt(monthsInput.value) || 6;
    const obs = obsInput.value.trim();

    if (!name || value <= 0) {
        alert('Informe nome e valor válido');
        return;
    }

    if (editingCosmeticProcedureIndex !== null) {
        cosmeticProcedures[editingCosmeticProcedureIndex] = { name, value, months, observations: obs };
        editingCosmeticProcedureIndex = null;
    } else {
        cosmeticProcedures.push({ name, value, months, observations: obs });
    }

    nameInput.value = ''; valueInput.value = ''; monthsInput.value = '6'; obsInput.value = '';
    renderCosmeticProcedures();
    renderCosmeticConduct();
    updateCosmeticTotal();
}

function removeCosmeticProcedure(index) {
    cosmeticProcedures.splice(index, 1);
    renderCosmeticProcedures();
    renderCosmeticConduct();
    updateCosmeticTotal();
}

function editCosmeticProcedure(index) {
    const proc = cosmeticProcedures[index];
    document.getElementById('newProcedureName').value = proc.name;
    document.getElementById('newProcedureValue').value = proc.value;
    document.getElementById('newProcedureMonths').value = proc.months;
    document.getElementById('newProcedureObservations').value = proc.observations || '';
    editingCosmeticProcedureIndex = index;
    bootstrap.Collapse.getOrCreateInstance(document.getElementById('cosmeticPlanCollapse')).show();
}

function renderCosmeticConduct() {
    const tbody = document.getElementById('cosmeticConductBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    cosmeticProcedures.forEach((proc, index) => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td class="ps-3">${proc.name}</td>
            <td>R$ ${proc.value.toFixed(2)}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-danger py-0 px-2 fw-bold" onclick="performCosmeticProcedure(${proc.id || 0}, '${proc.name}')">PENDENTE</button>
            </td>
        `;
    });
}

// ========== OUTRAS FUNÇÕES ==========
function loadPrescriptionHistory() {
    const container = document.getElementById('prescriptionHistory');
    if (!container) return;
    fetch(`/api/patient/${patientId}/prescriptions`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                if (data.prescriptions.length === 0) {
                    container.innerHTML = '<div class="text-center py-4 text-muted">Nenhuma receita emitida.</div>';
                    return;
                }
                let html = '<div class="list-group list-group-flush">';
                data.prescriptions.forEach(p => {
                    html += `<div class="list-group-item">
                        <div class="d-flex justify-content-between">
                            <strong>${p.date}</strong>
                            <a href="/receita/print/${p.id}" target="_blank" class="btn btn-sm btn-outline-primary">Ver</a>
                        </div>
                    </div>`;
                });
                html += '</div>';
                container.innerHTML = html;
            }
        });
}

function showAlert(message, type = 'success') {
    const placeholder = document.getElementById('alertPlaceholder');
    if (!placeholder) { alert(message); return; }
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show shadow-sm" role="alert">
        <div>${message}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
    placeholder.append(wrapper);
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(wrapper.firstElementChild);
        if (alert) alert.close();
    }, 5000);
}

function saveNote(type) {
    const payload = {
        type: type,
        queixa: document.getElementById('queixaText').value,
        anamnese: document.getElementById('anamneseText').value,
        diagnostico: document.getElementById('diagnosticoText').value,
        conduta: document.getElementById('condutaText').value,
        category: currentCategory,
        appointment_id: window.appointmentId
    };
    fetch(`/api/prontuario/${patientId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(r => r.json()).then(data => {
        if (data.success) showAlert('Salvo com sucesso!');
        else showAlert(data.error, 'danger');
    });
}

function savePatientTags() {
    const tags = Array.from(document.querySelectorAll('.tag-checkbox:checked')).map(cb => cb.value);
    fetch(`/api/patient/${patientId}/tags`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tags })
    }).then(r => r.json()).then(data => {
        if (data.success) showAlert('Tags atualizadas!');
    });
}

function finishConsultation() {
    if (!confirm('Finalizar consulta?')) return;
    const duration = timerStartTime ? Math.floor((Date.now() - timerStartTime) / 60000) : 0;
    fetch(`/api/prontuario/${patientId}/finalizar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            appointment_id: window.appointmentId,
            duration: duration,
            category: currentCategory,
            queixa: document.getElementById('queixaText').value,
            anamnese: document.getElementById('anamneseText').value,
            diagnostico: document.getElementById('diagnosticoText').value,
            conduta: document.getElementById('condutaText').value
        })
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Consulta finalizada!');
            setTimeout(() => window.location.href = '/agenda', 1000);
        }
    });
}

function updatePatientStars(stars) {
    fetch(`/api/patients/${patientId}/ivp`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ivp_stars: stars, ivp_manual_override: true })
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showAlert('Classificação atualizada!');
            location.reload();
        }
    });
}

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', function() {
    const categoryInputs = document.querySelectorAll('input[name="category"]');
    categoryInputs.forEach(input => {
        input.addEventListener('change', handleCategoryChange);
    });
    
    const activeCategory = document.querySelector('input[name="category"]:checked');
    if (activeCategory) {
        handleCategoryChange({ target: activeCategory });
    }

    loadPrescriptionHistory();
    // loadTimeline e loadExistingPlans foram removidos para simplificar e garantir funcionamento base
});
