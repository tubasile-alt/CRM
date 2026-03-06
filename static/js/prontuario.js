console.log('prontuario.js carregado v=20260305-6');
let timerInterval = null;
let timerStartTime = null;
let recognition = null;
let activeTextarea = null;

// ========== MENSAGENS CROSS-WINDOW ==========
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'prescription_saved') {
        showAlert('Receita salva com sucesso no prontuário!', 'success');
        loadPrescriptionHistory();

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
        showAlert('Erro no reconhecimento de voz. Verifique se o microfone está habilitado.', 'danger');
    };

    recognition.onend = function() {
        stopDictation();
    };
}

// FIX: recebe event como parâmetro explícito para evitar dependência de global implícito
function startDictation(textareaId, event) {
    if (!recognition) {
        showAlert('Reconhecimento de voz não suportado neste navegador.', 'warning');
        return;
    }

    activeTextarea = document.getElementById(textareaId);
    if (!activeTextarea) {
        showAlert('Campo de texto não encontrado.', 'danger');
        return;
    }

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
            showAlert('Erro ao iniciar ditado.', 'danger');
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

// ========== CLASSIFICAÇÃO DO PACIENTE ==========
function updatePatientStars(stars) {
    fetch(`/api/patients/${patientId}/ivp`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ ivp_stars: stars, ivp_manual_override: true })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showAlert('Classificação atualizada!', 'success');
            const container = document.getElementById('patientStarsContainer');
            container.innerHTML = stars ? `<span class="text-warning">${'⭐'.repeat(stars)}</span>` : '';
        } else {
            showAlert(data.error || 'Erro ao atualizar classificação', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao atualizar classificação', 'danger');
    });
}

function recalculateEvolution(appointmentId) {
    if (!appointmentId) {
        showAlert('ID da consulta não encontrado', 'warning');
        return;
    }
    if (!confirm('Deseja regerar a evolução para esta consulta?')) return;

    fetch(`/api/admin/recalculate-evolution/${appointmentId}`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showAlert('Evolução regerada com sucesso!', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert(data.error || 'Erro ao regerar evolução', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro de conexão', 'danger');
    });
}

// ========== TIMELINE / SCROLL ==========
function scrollToConsultation(id) {
    let el = document.getElementById(id);
    if (!el && typeof id === 'string' && id.startsWith('consultation-')) {
        el = document.getElementById(id.replace('consultation-', 'consult-'));
    }
    if (!el) return;

    const collapseEl = el.querySelector('.accordion-collapse');
    if (collapseEl && !collapseEl.classList.contains('show')) {
        new bootstrap.Collapse(collapseEl, { toggle: false }).show();
    }

    const historicoCard = el.closest('.card');
    if (historicoCard) historicoCard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    setTimeout(() => {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        el.classList.add('timeline-highlight');
        setTimeout(() => el.classList.remove('timeline-highlight'), 2000);
    }, 350);
}

function handleTimelineClick(el) {
    const apptId = el.dataset.appointmentId;
    const dtIso = el.dataset.dtIso;

    if (dtIso && isNaN(new Date(dtIso).getTime())) {
        console.error("Data inválida na timeline:", dtIso);
        showAlert("Data inválida para este evento", "warning");
        return;
    }

    const popover = el.nextElementSibling;
    if (popover) {
        const isVisible = popover.style.display === 'block';
        document.querySelectorAll('.timeline-popover').forEach(p => p.style.display = 'none');
        popover.style.display = isVisible ? 'none' : 'block';
    }

    if (!apptId || apptId === 'None' || apptId === 'null') return;

    const target = document.getElementById(`consultation-${apptId}`)
                || document.getElementById(`consult-${apptId}`)
                || document.getElementById(`evolution-${apptId}`);

    if (target) {
        performScrollAndHighlight(target, apptId);
    } else {
        let attempts = 0;
        const interval = setInterval(() => {
            const retryTarget = document.getElementById(`consultation-${apptId}`)
                             || document.getElementById(`consult-${apptId}`);
            if (retryTarget) {
                clearInterval(interval);
                performScrollAndHighlight(retryTarget, apptId);
            }
            if (++attempts >= 5) clearInterval(interval);
        }, 300);
    }
}

function performScrollAndHighlight(target, apptId) {
    const collapseEl = document.getElementById(`collapse${apptId}`);
    if (collapseEl && !collapseEl.classList.contains('show')) {
        new bootstrap.Collapse(collapseEl, { toggle: false }).show();
    }
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    target.classList.add('timeline-highlight');
    setTimeout(() => target.classList.remove('timeline-highlight'), 2000);
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

function getConsultationDuration() {
    return timerStartTime ? Math.floor((Date.now() - timerStartTime) / 60000) : null;
}

// ========== ALERTAS ==========
function showAlert(message, type = 'success') {
    const alertPlaceholder = document.getElementById('alertPlaceholder');
    if (!alertPlaceholder) {
        alert(message);
        return;
    }
    const wrapper = document.createElement('div');
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible fade show shadow-sm" role="alert">`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('');
    alertPlaceholder.append(wrapper);
    setTimeout(() => {
        bootstrap.Alert.getOrCreateInstance(wrapper.firstElementChild).close();
    }, 5000);
}

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content || '';
}

// ========== GESTÃO DE CATEGORIAS ==========
let currentCategory = 'patologia';
let cosmeticProcedures = [];
let groupedCosmeticPlans = [];
let editingCosmeticProcedureIndex = null;

async function loadExistingPlans() {
    if (!patientId) return;
    try {
        const response = await fetch(`/api/prontuario/${patientId}/cosmetic-plans-grouped`);
        if (!response.ok) return;
        const data = await response.json();

        if (data.success && data.grouped_plans && data.grouped_plans.length > 0) {
            groupedCosmeticPlans = data.grouped_plans;
            cosmeticProcedures = [];

            data.grouped_plans.forEach(group => {
                group.procedures.forEach(plan => {
                    cosmeticProcedures.push({
                        id: plan.id,
                        name: plan.procedure_name,
                        value: parseFloat(plan.planned_value) || 0,
                        months: plan.follow_up_months || 6,
                        budget: parseFloat(plan.final_budget || plan.planned_value) || 0,
                        performed: !!plan.was_performed,
                        performedDate: plan.performed_date || null,
                        observations: plan.observations || '',
                        consultationKey: group.consultation_key || null,
                        consultationDate: group.consultation_info?.display_date || '',
                        appointmentId: group.appointment_id || plan.appointment_id || null
                    });
                });
            });

            if (document.getElementById('cosmeticPlanBody')) {
                renderCosmeticProcedures();
                renderCosmeticConduct();
                updateCosmeticTotal();
            }
        }
    } catch (error) {
        console.error('Erro ao carregar planejamentos:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(loadExistingPlans, 500);
    setTimeout(loadPrescriptionHistory, 500);
    loadTimeline();
});
