let timerInterval = null;
let timerStartTime = null;
let recognition = null;
let activeTextarea = null;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.continuous = true;
    recognition.interimResults = true;
    
    recognition.onresult = function(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        if (activeTextarea && finalTranscript) {
            activeTextarea.value += finalTranscript;
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

function startDictation(textareaId) {
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
            recognition.start();
            button.classList.add('dictation-active');
            button.innerHTML = '<i class="bi bi-mic-fill"></i> Gravando...';
        } catch (error) {
            console.error('Erro ao iniciar ditado:', error);
            showAlert('Erro ao iniciar ditado.', 'danger');
        }
    }
}

function stopDictation() {
    if (recognition) {
        recognition.stop();
    }
    
    const buttons = document.querySelectorAll('.dictation-active');
    buttons.forEach(button => {
        button.classList.remove('dictation-active');
        button.innerHTML = '<i class="bi bi-mic"></i> Ditado';
    });
    
    activeTextarea = null;
}

function startConsultation() {
    const button = document.getElementById('startTimer');
    const display = document.getElementById('timerDisplay');
    
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        button.innerHTML = '<i class="bi bi-play-circle"></i> Iniciar Atendimento';
        button.classList.remove('btn-danger');
        button.classList.add('btn-success');
        display.classList.remove('timer-running');
    } else {
        timerStartTime = Date.now();
        button.innerHTML = '<i class="bi bi-stop-circle"></i> Parar Atendimento';
        button.classList.remove('btn-success');
        button.classList.add('btn-danger');
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
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function getConsultationDuration() {
    if (timerStartTime) {
        return Math.floor((Date.now() - timerStartTime) / 60000);
    }
    return null;
}

function saveNote(noteType) {
    const textareaId = `${noteType}Text`;
    const content = document.getElementById(textareaId).value.trim();
    
    if (!content) {
        showAlert('Por favor, adicione algum conteúdo antes de salvar.', 'warning');
        return;
    }
    
    const data = {
        type: noteType,
        content: content,
        duration: getConsultationDuration()
    };
    
    if (noteType === 'anamnese') {
        const indicatedProcs = Array.from(document.querySelectorAll('.indicated-proc:checked'))
            .map(cb => parseInt(cb.value));
        if (indicatedProcs.length > 0) {
            data.indicated_procedures = indicatedProcs;
        }
    }
    
    if (noteType === 'conduta') {
        const performedProcs = Array.from(document.querySelectorAll('.performed-proc:checked'))
            .map(cb => parseInt(cb.value));
        if (performedProcs.length > 0) {
            data.performed_procedures = performedProcs;
        }
    }
    
    fetch(`/api/prontuario/${patientId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Anotação salva com sucesso!');
            document.getElementById(textareaId).value = '';
            
            if (noteType === 'anamnese') {
                document.querySelectorAll('.indicated-proc').forEach(cb => cb.checked = false);
            }
            if (noteType === 'conduta') {
                document.querySelectorAll('.performed-proc').forEach(cb => cb.checked = false);
            }
            
            setTimeout(() => location.reload(), 1500);
        }
    })
    .catch(error => {
        showAlert('Erro ao salvar anotação.', 'danger');
        console.error(error);
    });
}

function savePatientTags() {
    const selectedTags = Array.from(document.querySelectorAll('.tag-checkbox:checked'))
        .map(cb => parseInt(cb.value));
    
    fetch(`/api/patient/${patientId}/tags`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tags: selectedTags })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Tags atualizadas com sucesso!');
        }
    })
    .catch(error => {
        showAlert('Erro ao atualizar tags.', 'danger');
        console.error(error);
    });
}

// ========== GESTÃO DE CATEGORIAS ==========
let currentCategory = 'patologia';
let cosmeticProcedures = [];

document.addEventListener('DOMContentLoaded', function() {
    // Listener para mudança de categoria
    const categoryInputs = document.querySelectorAll('input[name="category"]');
    categoryInputs.forEach(input => {
        input.addEventListener('change', handleCategoryChange);
    });
    
    // Inicializar textos pré-preenchidos
    updateCategoryTexts();
});

function handleCategoryChange(event) {
    currentCategory = event.target.value;
    updateCategoryTexts();
    toggleCategoryTabs();
}

function updateCategoryTexts() {
    const queixaText = document.getElementById('queixaText');
    const anamneseText = document.getElementById('anamneseText');
    const condutaText = document.getElementById('condutaText');
    
    if (currentCategory === 'cosmiatria') {
        // Preencher anamnese padrão para cosmiatria
        if (!anamneseText.value) {
            anamneseText.value = 'Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.';
        }
    } else if (currentCategory === 'transplante_capilar') {
        // Preencher queixa padrão para transplante
        if (!queixaText.value) {
            queixaText.value = 'Paciente refere queixa de rarefação capilar e calvície progressiva.';
        }
        // Preencher conduta padrão para transplante
        if (!condutaText.value) {
            condutaText.value = 'O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n';
        }
    }
}

function toggleCategoryTabs() {
    const tabPlanejamento = document.getElementById('tabPlanejamento');
    const tabTransplante = document.getElementById('tabTransplante');
    const conductProcedures = document.getElementById('conductProceduresSection');
    
    if (currentCategory === 'cosmiatria') {
        tabPlanejamento.style.display = '';
        tabTransplante.style.display = 'none';
        if (conductProcedures) conductProcedures.style.display = 'none';
    } else if (currentCategory === 'transplante_capilar') {
        tabPlanejamento.style.display = 'none';
        tabTransplante.style.display = '';
        if (conductProcedures) conductProcedures.style.display = 'none';
    } else {
        tabPlanejamento.style.display = 'none';
        tabTransplante.style.display = 'none';
        if (conductProcedures) conductProcedures.style.display = '';
    }
}

// ========== COSMIATRIA: PLANEJAMENTO CLÍNICO ==========
function addCosmeticProcedure() {
    const name = document.getElementById('newProcedureName').value;
    const value = parseFloat(document.getElementById('newProcedureValue').value) || 0;
    const months = parseInt(document.getElementById('newProcedureMonths').value) || 6;
    
    if (!name) {
        showAlert('Selecione um procedimento', 'warning');
        return;
    }
    
    if (value <= 0) {
        showAlert('Informe um valor válido', 'warning');
        return;
    }
    
    cosmeticProcedures.push({ name, value, months });
    renderCosmeticProcedures();
    updateCosmeticTotal();
    
    // Limpar campos
    document.getElementById('newProcedureName').value = '';
    document.getElementById('newProcedureValue').value = '';
    document.getElementById('newProcedureMonths').value = '6';
}

function removeCosmeticProcedure(index) {
    cosmeticProcedures.splice(index, 1);
    renderCosmeticProcedures();
    updateCosmeticTotal();
}

function renderCosmeticProcedures() {
    const tbody = document.getElementById('cosmeticPlanBody');
    tbody.innerHTML = '';
    
    cosmeticProcedures.forEach((proc, index) => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${proc.name}</td>
            <td class="text-end">R$ ${proc.value.toFixed(2).replace('.', ',')}</td>
            <td class="text-center">${proc.months} meses</td>
            <td class="text-center">
                <button class="btn btn-sm btn-danger" onclick="removeCosmeticProcedure(${index})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
    });
}

function updateCosmeticTotal() {
    const total = cosmeticProcedures.reduce((sum, proc) => sum + proc.value, 0);
    document.getElementById('cosmeticTotal').textContent = total.toFixed(2).replace('.', ',');
}

function saveCosmeticPlan() {
    if (cosmeticProcedures.length === 0) {
        showAlert('Adicione pelo menos um procedimento ao planejamento', 'warning');
        return;
    }
    
    const data = {
        category: 'cosmiatria',
        procedures: cosmeticProcedures,
        anamnese: document.getElementById('anamneseText').value,
        conduta: document.getElementById('condutaText').value
    };
    
    fetch(`/api/prontuario/${patientId}/cosmetic-plan`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Planejamento cosmético salvo com sucesso!');
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert(result.error || 'Erro ao salvar planejamento', 'danger');
        }
    })
    .catch(error => {
        showAlert('Erro ao salvar planejamento.', 'danger');
        console.error(error);
    });
}

function generateBudget() {
    if (cosmeticProcedures.length === 0) {
        showAlert('Adicione procedimentos ao planejamento antes de gerar o orçamento', 'warning');
        return;
    }
    
    const data = {
        procedures: cosmeticProcedures
    };
    
    fetch(`/api/prontuario/${patientId}/generate-budget`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `orcamento_${patientId}_${new Date().getTime()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showAlert('Orçamento PDF gerado com sucesso!');
    })
    .catch(error => {
        showAlert('Erro ao gerar orçamento.', 'danger');
        console.error(error);
    });
}

// ========== TRANSPLANTE CAPILAR ==========
let selectedNorwood = null;

function selectNorwood(classification) {
    // Remover seleção anterior
    document.querySelectorAll('.norwood-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Adicionar seleção atual
    const card = document.querySelector(`[data-norwood="${classification}"] .norwood-card`);
    if (card) {
        card.classList.add('selected');
        selectedNorwood = classification;
    }
}

function saveHairTransplant() {
    if (!selectedNorwood) {
        showAlert('Selecione a classificação de Norwood', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('category', 'transplante_capilar');
    formData.append('norwood', selectedNorwood);
    formData.append('case_type', document.querySelector('input[name="caseType"]:checked').value);
    formData.append('body_hair', document.getElementById('bodyHair').checked);
    formData.append('eyebrow_transplant', document.getElementById('eyebrowTransplant').checked);
    formData.append('beard_transplant', document.getElementById('beardTransplant').checked);
    formData.append('frontal', document.getElementById('frontalTransplant').checked);
    formData.append('crown', document.getElementById('crownTransplant').checked);
    formData.append('complete', document.getElementById('completeTransplant').checked);
    formData.append('complete_body_hair', document.getElementById('completeBodyHair').checked);
    formData.append('surgical_planning', document.getElementById('surgicalPlanning').value);
    formData.append('queixa', document.getElementById('queixaText').value);
    formData.append('conduta', document.getElementById('condutaText').value);
    
    // Imagens
    const consultationPhoto = document.getElementById('consultationPhoto').files[0];
    const surgicalPlan = document.getElementById('surgicalPlanImage').files[0];
    const simulation = document.getElementById('simulationImage').files[0];
    
    if (!consultationPhoto) {
        showAlert('Foto da consulta é obrigatória', 'warning');
        return;
    }
    
    formData.append('consultation_photo', consultationPhoto);
    if (surgicalPlan) formData.append('surgical_plan', surgicalPlan);
    if (simulation) formData.append('simulation', simulation);
    
    fetch(`/api/prontuario/${patientId}/hair-transplant`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Dados de transplante capilar salvos com sucesso!');
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert(result.error || 'Erro ao salvar dados', 'danger');
        }
    })
    .catch(error => {
        showAlert('Erro ao salvar dados de transplante.', 'danger');
        console.error(error);
    });
}
