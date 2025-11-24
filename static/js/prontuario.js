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
        
        // Atualizar o campo com a transcrição final
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

function startDictation(textareaId) {
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
            // Resetar o reconhecimento antes de iniciar
            if (recognition) {
                recognition.stop();
                setTimeout(() => {
                    recognition.start();
                }, 100);
            }
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
let groupedCosmeticPlans = [];

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
                        performed: plan.was_performed || false,
                        performedDate: plan.performed_date || null,
                        consultationKey: group.consultation_key,
                        consultationDate: group.consultation_info.display_date
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
    // Carregar planos existentes ao iniciar
    setTimeout(loadExistingPlans, 500);
    
    // Listener para mudança de categoria
    const categoryInputs = document.querySelectorAll('input[name="category"]');
    categoryInputs.forEach(input => {
        input.addEventListener('change', handleCategoryChange);
    });
    
    // Inicializar textos pré-preenchidos
    updateCategoryTexts();
});

function handleCategoryChange(event) {
    const newCategory = event.target.value;
    
    // Para Cosmiatria e Transplante Capilar: auto-iniciar o timer
    if (newCategory === 'cosmiatria' || newCategory === 'transplante_capilar') {
        if (!timerStartTime) {
            // Auto-iniciar o atendimento
            startConsultation();
        }
    } else if (newCategory === 'patologia') {
        // Para Patologia: requerer clique manual
        if (!timerStartTime) {
            event.preventDefault();
            alert('⚠️ Por favor, inicie o atendimento antes de selecionar a categoria.\n\nClique no botão "Iniciar Atendimento" no topo da página.');
            // Reverter para categoria anterior
            const previousRadio = document.querySelector(`input[name="category"][value="${currentCategory}"]`);
            if (previousRadio) {
                previousRadio.checked = true;
            }
            return;
        }
    }
    
    currentCategory = newCategory;
    updateCategoryTexts();
    toggleCategoryTabs();
    
    // Se mudou para Cosmiatria e ainda não carregou os planos, carregar agora
    if (currentCategory === 'cosmiatria' && cosmeticProcedures.length === 0) {
        loadExistingPlans();
    }
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
    const cosmeticConductSection = document.getElementById('cosmeticConductSection');
    const indicatedProcedures = document.getElementById('indicatedProceduresSection');
    
    if (currentCategory === 'cosmiatria') {
        tabPlanejamento.style.display = '';
        tabTransplante.style.display = 'none';
        if (conductProcedures) conductProcedures.style.display = 'none';
        if (cosmeticConductSection) cosmeticConductSection.style.display = '';
        if (indicatedProcedures) indicatedProcedures.style.display = 'none';
    } else if (currentCategory === 'transplante_capilar') {
        tabPlanejamento.style.display = 'none';
        tabTransplante.style.display = '';
        if (conductProcedures) conductProcedures.style.display = 'none';
        if (cosmeticConductSection) cosmeticConductSection.style.display = 'none';
        if (indicatedProcedures) indicatedProcedures.style.display = 'none';
    } else {
        // Patologia - NÃO mostra checkboxes de procedimentos realizados
        tabPlanejamento.style.display = 'none';
        tabTransplante.style.display = 'none';
        if (conductProcedures) conductProcedures.style.display = 'none';  // OCULTADO
        if (cosmeticConductSection) cosmeticConductSection.style.display = 'none';
        if (indicatedProcedures) indicatedProcedures.style.display = '';
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
    
    cosmeticProcedures.push({ name, value, months, budget: value, performed: false });
    renderCosmeticProcedures();
    renderCosmeticConduct();
    updateCosmeticTotal();
    
    // Limpar campos
    document.getElementById('newProcedureName').value = '';
    document.getElementById('newProcedureValue').value = '';
    document.getElementById('newProcedureMonths').value = '6';
}

function removeCosmeticProcedure(index) {
    cosmeticProcedures.splice(index, 1);
    renderCosmeticProcedures();
    renderCosmeticConduct();
    updateCosmeticTotal();
}

function highlightConsultationGroup(consultationKey) {
    if (currentCategory !== 'cosmiatria') {
        return;
    }
    
    setTimeout(() => {
        const groupElement = document.getElementById(`group-${consultationKey}`);
        if (groupElement) {
            document.querySelectorAll('.consultation-group-header').forEach(el => {
                el.classList.remove('highlighted-group');
            });
            
            groupElement.classList.add('highlighted-group');
            groupElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            setTimeout(() => {
                groupElement.classList.remove('highlighted-group');
            }, 3000);
        }
    }, 300);
}

function renderCosmeticProcedures() {
    const tbody = document.getElementById('cosmeticPlanBody');
    tbody.innerHTML = '';
    
    const newProcedures = cosmeticProcedures.filter(p => !p.id);
    
    if (newProcedures.length > 0) {
        const headerRow = tbody.insertRow();
        headerRow.className = 'consultation-group-header';
        headerRow.id = 'group-new';
        headerRow.innerHTML = `
            <td colspan="4" class="bg-success bg-opacity-10 border-top border-bottom border-2 border-success">
                <div class="d-flex align-items-center py-2">
                    <i class="bi bi-plus-circle me-2 text-success"></i>
                    <strong class="text-success">Nova Consulta (não salvo)</strong>
                    <span class="ms-2 text-muted small">(${newProcedures.length} procedimento${newProcedures.length > 1 ? 's' : ''})</span>
                </div>
            </td>
        `;
        
        newProcedures.forEach(proc => {
            const globalIndex = cosmeticProcedures.findIndex(p => p === proc);
            const row = tbody.insertRow();
            row.className = 'consultation-group-item';
            row.innerHTML = `
                <td class="ps-4">${proc.name}</td>
                <td class="text-end">R$ ${proc.value.toFixed(2).replace('.', ',')}</td>
                <td class="text-center">${proc.months} meses</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-primary me-1" onclick="editCosmeticProcedure(${globalIndex})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="removeCosmeticProcedure(${globalIndex})" title="Remover">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
        });
    }
    
    if (groupedCosmeticPlans.length === 0 && newProcedures.length === 0) {
        return;
    }
    
    groupedCosmeticPlans.forEach(group => {
        const headerRow = tbody.insertRow();
        headerRow.className = 'consultation-group-header';
        headerRow.id = `group-${group.consultation_key}`;
        headerRow.innerHTML = `
            <td colspan="4" class="bg-light border-top border-bottom border-2">
                <div class="d-flex align-items-center py-2">
                    <i class="bi bi-calendar3 me-2 text-primary"></i>
                    <strong>Consulta de ${group.consultation_info.display_date}</strong>
                    <span class="ms-2 text-muted small">(${group.procedures.length} procedimento${group.procedures.length > 1 ? 's' : ''})</span>
                </div>
            </td>
        `;
        
        group.procedures.forEach(proc => {
            const globalIndex = cosmeticProcedures.findIndex(p => p.id === proc.id);
            const row = tbody.insertRow();
            row.className = 'consultation-group-item';
            row.innerHTML = `
                <td class="ps-4">${proc.procedure_name}</td>
                <td class="text-end">R$ ${parseFloat(proc.planned_value).toFixed(2).replace('.', ',')}</td>
                <td class="text-center">${proc.follow_up_months} meses</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-primary me-1" onclick="editCosmeticProcedure(${globalIndex})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="removeCosmeticProcedure(${globalIndex})" title="Remover">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
        });
    });
}

function editCosmeticProcedure(index) {
    const proc = cosmeticProcedures[index];
    
    // Preencher os campos do formulário com os dados do procedimento
    document.getElementById('newProcedureName').value = proc.name;
    document.getElementById('newProcedureValue').value = proc.value;
    document.getElementById('newProcedureMonths').value = proc.months;
    
    // Remover o procedimento antigo da lista
    cosmeticProcedures.splice(index, 1);
    
    // Atualizar as visualizações
    renderCosmeticProcedures();
    renderCosmeticConduct();
    updateCosmeticTotal();
    
    // Focar no botão de adicionar
    document.getElementById('newProcedureName').focus();
    
    showAlert('Procedimento carregado para edição. Modifique os dados e clique em "Adicionar ao Planejamento".', 'info');
}

function updateCosmeticTotal() {
    const total = cosmeticProcedures.reduce((sum, proc) => sum + proc.value, 0);
    document.getElementById('cosmeticTotal').textContent = total.toFixed(2).replace('.', ',');
}

// ========== COSMIATRIA: ABA CONDUTA - EXECUÇÃO ==========
function renderCosmeticConduct() {
    const tbody = document.getElementById('cosmeticConductBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    cosmeticProcedures.forEach((proc, index) => {
        // Apenas usar data se o procedimento foi realizado E tem data definida
        const procedureDate = proc.performedDate || '';
        
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${proc.name}</td>
            <td>
                <input type="number" 
                       class="form-control form-control-sm" 
                       value="${proc.budget || proc.value}" 
                       onchange="updateProcedureBudget(${index}, this.value)"
                       step="any" min="0">
            </td>
            <td>
                <input type="date" 
                       class="form-control form-control-sm" 
                       value="${procedureDate}"
                       onchange="updateProcedureDate(${index}, this.value)"
                       ${!proc.performed ? 'disabled' : ''}
                       placeholder="${proc.performed ? 'Selecione a data' : ''}">
            </td>
            <td class="text-center">
                <button class="btn btn-sm ${proc.performed ? 'btn-success' : 'btn-outline-secondary'}" 
                        onclick="toggleProcedurePerformed(${index})">
                    <i class="bi ${proc.performed ? 'bi-check-circle-fill' : 'bi-circle'}"></i>
                    ${proc.performed ? 'Feito' : 'Não Feito'}
                </button>
            </td>
        `;
    });
}

function updateProcedureBudget(index, value) {
    cosmeticProcedures[index].budget = parseFloat(value) || 0;
}

function updateProcedureDate(index, dateValue) {
    cosmeticProcedures[index].performedDate = dateValue;
}

function toggleProcedurePerformed(index) {
    cosmeticProcedures[index].performed = !cosmeticProcedures[index].performed;
    
    // Se marcou como "Feito" e não tem data, definir hoje como padrão
    if (cosmeticProcedures[index].performed && !cosmeticProcedures[index].performedDate) {
        cosmeticProcedures[index].performedDate = new Date().toISOString().split('T')[0];
    }
    
    // Se desmarcou como "Feito", limpar a data
    if (!cosmeticProcedures[index].performed) {
        cosmeticProcedures[index].performedDate = null;
    }
    
    renderCosmeticConduct();
}

function saveCosmeticPlan() {
    // DEPRECATED: Não salvar mais - dados são salvos ao finalizar
    // Apenas mostrar mensagem informativa
    alert('Os procedimentos são salvos automaticamente ao clicar em "Finalizar Atendimento" na aba Conduta.\n\nUse o botão "Gerar Orçamento PDF" se precisar enviar o orçamento ao paciente.');
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

function toggleTransplantLocation() {
    const previousYes = document.getElementById('previousYes');
    const locationSection = document.getElementById('transplantLocationSection');
    
    if (previousYes && previousYes.checked) {
        locationSection.style.display = '';
    } else {
        locationSection.style.display = 'none';
    }
}

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
    formData.append('previous_transplant', document.querySelector('input[name="previousTransplant"]:checked').value);
    
    // Se já fez transplante, adicionar local
    const previousYes = document.getElementById('previousYes');
    if (previousYes && previousYes.checked) {
        const location = document.querySelector('input[name="transplantLocation"]:checked');
        if (location) {
            formData.append('transplant_location', location.value);
        }
    }
    
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

// ========== FINALIZAR ATENDIMENTO ==========
function finalizarAtendimento() {
    // Verificar se o atendimento foi iniciado
    if (!timerStartTime) {
        alert('É necessário iniciar o atendimento antes de finalizar!');
        return;
    }
    
    // Confirmar finalização
    if (!confirm('Deseja finalizar o atendimento? Todos os dados serão salvos.')) {
        return;
    }
    
    // Calcular duração em minutos
    const duration = Math.floor((Date.now() - timerStartTime) / 60000);
    
    // Coletar dados dos campos de texto
    const queixa = document.getElementById('queixaText')?.value || '';
    const anamnese = document.getElementById('anamneseText')?.value || '';
    const diagnostico = document.getElementById('diagnosticoText')?.value || '';
    const conduta = document.getElementById('condutaText')?.value || '';
    
    // Coletar procedimentos indicados e realizados (Patologia)
    const indicated = Array.from(document.querySelectorAll('.indicated-proc:checked')).map(cb => parseInt(cb.value));
    const performed = Array.from(document.querySelectorAll('.performed-proc:checked')).map(cb => parseInt(cb.value));
    
    // Montar payload base
    const payload = {
        consultation_started: true,
        category: currentCategory,
        duration: duration,
        queixa: queixa,
        anamnese: anamnese,
        diagnostico: diagnostico,
        conduta: conduta,
        indicated_procedures: indicated,
        performed_procedures: performed,
        consultation_type: document.querySelector('input[name="patient_type"]')?.value || 'Particular'
    };
    
    // Incluir appointment_id se disponível
    if (typeof appointmentId !== 'undefined' && appointmentId !== null) {
        payload.appointment_id = appointmentId;
    }
    
    // Adicionar dados específicos de Cosmiatria
    if (currentCategory === 'cosmiatria' && cosmeticProcedures.length > 0) {
        payload.cosmetic_procedures = cosmeticProcedures;
        
        // Calcular total dos procedimentos realizados
        const performedProcedures = cosmeticProcedures.filter(p => p.performed);
        const totalPerformed = performedProcedures.reduce((sum, p) => sum + (parseFloat(p.budget) || parseFloat(p.value)), 0);
        
        if (totalPerformed > 0) {
            payload.checkout_amount = totalPerformed;
            payload.checkout_procedures = performedProcedures.map(p => ({
                name: p.name,
                value: parseFloat(p.budget) || parseFloat(p.value),
                budget: parseFloat(p.budget) || parseFloat(p.value)
            }));
            console.log('Checkout criado:', { amount: totalPerformed, procedures: payload.checkout_procedures });
        }
    }
    
    // Adicionar dados específicos de Transplante Capilar
    if (currentCategory === 'transplante_capilar') {
        const previousTransplant = document.querySelector('input[name="previousTransplant"]:checked')?.value || 'nao';
        const transplantLocation = document.querySelector('input[name="transplantLocation"]:checked')?.value || '';
        const norwood = document.getElementById('norwoodClassification')?.value || '';
        const surgicalPlanning = document.getElementById('surgicalPlanning')?.value || '';
        
        payload.transplant_data = {
            norwood: norwood,
            previous_transplant: previousTransplant,
            transplant_location: transplantLocation,
            frontal: document.getElementById('frontalTransplant')?.checked || false,
            crown: document.getElementById('crownTransplant')?.checked || false,
            complete: document.getElementById('completeTransplant')?.checked || false,
            complete_body_hair: document.getElementById('completeBodyHair')?.checked || false,
            surgical_planning: surgicalPlanning
        };
    }
    
    // Mostrar loading
    const btn = document.querySelector('button[onclick="finalizarAtendimento()"]');
    if (btn) {
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Finalizando...';
        
        // Enviar para o backend
        fetch(`/api/prontuario/${patientId}/finalizar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                // Parar cronômetro
                if (timerInterval) {
                    clearInterval(timerInterval);
                    timerInterval = null;
                }
                timerStartTime = null;
                
                alert('Atendimento finalizado com sucesso!');
                
                // Redirecionar de volta para a agenda
                window.location.href = '/agenda';
            } else {
                alert(result.error || 'Erro ao finalizar atendimento');
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao finalizar atendimento. Por favor, tente novamente.');
            btn.disabled = false;
            btn.innerHTML = originalText;
        });
    }
}
