let timerInterval = null;
let timerStartTime = null;
let recognition = null;
let activeTextarea = null;

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

function finishConsultation() {
    if (!timerStartTime) {
        showAlert('O atendimento ainda não foi iniciado.', 'warning');
        return;
    }

    const duration = getConsultationDuration();
    
    if (confirm(`Deseja finalizar o atendimento? Duração total: ${duration} minutos.`)) {
        fetch(`/api/prontuario/${patientId}/finalizar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                duration: duration,
                appointment_id: window.appointmentId,
                consultation_started: true
            })
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
                
                const button = document.getElementById('startTimer');
                const display = document.getElementById('timerDisplay');
                if (button) {
                    button.innerHTML = '<i class="bi bi-play-circle"></i> Iniciar Atendimento';
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-success');
                }
                if (display) {
                    display.textContent = '00:00';
                    display.classList.remove('timer-running');
                }
                
                showAlert('Atendimento finalizado com sucesso!', 'success');
                setTimeout(() => {
                    window.location.href = '/agenda';
                }, 1500);
            }
        })
        .catch(error => {
            console.error('Erro ao finalizar atendimento:', error);
            showAlert('Erro ao finalizar atendimento.', 'danger');
        });
    }
}

function saveNote(noteType) {
    const textareaId = `${noteType}Text`;
    const content = document.getElementById(textareaId).value.trim();
    
    // Auto-iniciar cronômetro se ainda não começou
    if (!timerStartTime) {
        startConsultation();
    }

    if (!content) {
        showAlert('Por favor, adicione algum conteúdo antes de salvar.', 'warning');
        return;
    }
    
    const data = {
        type: noteType,
        content: content,
        duration: getConsultationDuration(),
        appointment_id: window.appointmentId,
        consultation_started: !!timerStartTime
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
    
    // Carregar histórico de receitas
    setTimeout(loadPrescriptionHistory, 500);
    
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
    const tabSurgery = document.getElementById('tabSurgery');
    const conductProcedures = document.getElementById('conductProceduresSection');
    const cosmeticConductSection = document.getElementById('cosmeticConductSection');
    const indicatedProcedures = document.getElementById('indicatedProceduresSection');
    
    if (currentCategory === 'cosmiatria') {
        tabPlanejamento.style.display = '';
        tabTransplante.style.display = 'none';
        if (tabSurgery) tabSurgery.style.display = 'none';
        if (conductProcedures) conductProcedures.style.display = 'none';
        if (cosmeticConductSection) cosmeticConductSection.style.display = '';
        if (indicatedProcedures) indicatedProcedures.style.display = 'none';
    } else if (currentCategory === 'transplante_capilar') {
        tabPlanejamento.style.display = 'none';
        tabTransplante.style.display = '';
        if (tabSurgery) tabSurgery.style.display = '';
        if (conductProcedures) conductProcedures.style.display = 'none';
        if (cosmeticConductSection) cosmeticConductSection.style.display = 'none';
        if (indicatedProcedures) indicatedProcedures.style.display = 'none';
    } else {
        // Patologia - NÃO mostra checkboxes de procedimentos realizados
        tabPlanejamento.style.display = 'none';
        tabTransplante.style.display = 'none';
        if (tabSurgery) tabSurgery.style.display = 'none';
        if (conductProcedures) conductProcedures.style.display = 'none';  // OCULTADO
        if (cosmeticConductSection) cosmeticConductSection.style.display = 'none';
        if (indicatedProcedures) indicatedProcedures.style.display = '';
    }
}

// ========== COSMIATRIA: PLANEJAMENTO CLÍNICO ==========
function performCosmeticProcedure(planId, procedureName) {
    console.log('performCosmeticProcedure called:', planId, procedureName);
    const today = new Date().toISOString().split('T')[0];
    const dateInput = prompt('Marcar "' + procedureName + '" como realizado em qual data? (AAAA-MM-DD)', today);
    
    if (!dateInput) return;

    fetch('/api/cosmetic-plans/' + planId + '/perform', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            appointment_id: window.appointmentId,
            performed_date: dateInput
        })
    })
    .then(function(r) {
        console.log('Response status:', r.status);
        return r.json();
    })
    .then(function(result) {
        console.log('Result:', result);
        if (result.success) {
            if (typeof showAlert === 'function') {
                showAlert('Procedimento marcado como realizado e evolução criada!', 'success');
            } else {
                alert('Procedimento marcado como realizado e evolução criada!');
            }
            setTimeout(function() { location.reload(); }, 1000);
        } else {
            var msg = result.error || 'Erro ao processar';
            if (typeof showAlert === 'function') {
                showAlert(msg, 'danger');
            } else {
                alert(msg);
            }
        }
    })
    .catch(function(err) {
        console.error('Erro na requisição:', err);
        if (typeof showAlert === 'function') {
            showAlert('Erro na comunicação com o servidor', 'danger');
        } else {
            alert('Erro na comunicação com o servidor');
        }
    });
}

function addCosmeticProcedure() {
    const nameInput = document.getElementById('newProcedureName');
    const valueInput = document.getElementById('newProcedureValue');
    const name = nameInput.value.trim();
    const valueStr = valueInput.value.trim();
    const value = valueStr ? parseFloat(valueStr) : 0;
    const months = parseInt(document.getElementById('newProcedureMonths').value) || 6;
    const observations = document.getElementById('newProcedureObservations').value || '';
    
    // Validação: nome não pode estar vazio
    if (!name || name === '') {
        alert('Por favor, selecione um procedimento');
        nameInput.focus();
        return;
    }
    
    // Validação: valor deve ser maior que 0
    if (isNaN(value) || value <= 0) {
        alert('Por favor, informe um valor válido (maior que 0)');
        valueInput.focus();
        return;
    }
    
    // Adicionar procedimento
    cosmeticProcedures.push({ name, value, months, budget: value, performed: false, observations });
    
    // Atualizar a renderização
    renderCosmeticProcedures();
    renderCosmeticConduct();
    updateCosmeticTotal();
    
    // Limpar campos
    nameInput.value = '';
    valueInput.value = '';
    document.getElementById('newProcedureMonths').value = '6';
    document.getElementById('newProcedureObservations').value = '';
    
    // Focar no próximo procedimento
    setTimeout(() => nameInput.focus(), 100);
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
                <td><small>${proc.observations || '-'}</small></td>
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
                <td><small>${proc.observations || '-'}</small></td>
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
    formData.append('feminine_hair_transplant', document.getElementById('feminineHairTransplant').checked);
    formData.append('frontal', document.getElementById('frontalTransplant').checked);
    formData.append('crown', document.getElementById('crownTransplant').checked);
    formData.append('complete', document.getElementById('completeTransplant').checked);
    formData.append('complete_body_hair', document.getElementById('completeBodyHair').checked);
    formData.append('dense_packing', document.getElementById('densePacking').checked);
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
    
    // Incluir appointment_id se disponível (usando window.appointmentId)
    if (typeof window.appointmentId !== 'undefined' && window.appointmentId !== null) {
        payload.appointment_id = window.appointmentId;
        console.log('DEBUG finalizarAtendimento: Enviando appointment_id =', window.appointmentId);
    } else {
        console.log('DEBUG finalizarAtendimento: ATENCAO - appointment_id NAO disponivel!');
    }
    
    // Adicionar indicação de transplante (na aba Conduta)
    const transplantIndication = document.querySelector('input[name="transplantIndication"]:checked');
    if (transplantIndication) {
        payload.transplant_indication = transplantIndication.value;
    }
    
    // Adicionar dados de planejamento cirúrgico se categoria é transplante
    if (currentCategory === 'transplante_capilar') {
        payload.surgical_planning = {
            norwood: document.querySelector('input[name="norwood"]:checked')?.value || null,
            previous_transplant: document.querySelector('input[name="previousTransplant"]:checked')?.value || 'nao',
            transplant_location: document.querySelector('input[name="transplantLocation"]:checked')?.value || null,
            case_type: document.querySelector('input[name="caseType"]:checked')?.value || 'primaria',
            body_hair: document.getElementById('bodyHair')?.checked || false,
            eyebrow_transplant: document.getElementById('eyebrowTransplant')?.checked || false,
            beard_transplant: document.getElementById('beardTransplant')?.checked || false,
            feminine_hair_transplant: document.getElementById('feminineHairTransplant')?.checked || false,
            frontal: document.getElementById('frontalTransplant')?.checked || false,
            crown: document.getElementById('crownTransplant')?.checked || false,
            complete: document.getElementById('completeTransplant')?.checked || false,
            complete_body_hair: document.getElementById('completeBodyHair')?.checked || false,
            dense_packing: document.getElementById('densePacking')?.checked || false,
            surgical_planning_text: document.getElementById('surgicalPlanning')?.value || ''
        };
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

// Auto-open attention modal if there's content when page loads
document.addEventListener('DOMContentLoaded', function() {
    const attentionContent = document.getElementById('attentionContent');
    if (attentionContent && attentionContent.textContent.trim()) {
        // Delay slightly to ensure page is fully loaded
        setTimeout(() => {
            const attentionText = document.getElementById('attentionText');
            if (attentionText) {
                attentionText.value = attentionContent.textContent;
                new bootstrap.Modal(document.getElementById('attentionModal')).show();
            }
        }, 300);
    }
});

// Editar data da consulta
function editConsultationDate(consultationId, dateTime) {
    document.getElementById('editConsultationId').value = consultationId;
    document.getElementById('editConsultationDateTime').value = dateTime;
    
    // Carregar notas da consulta
    fetch(`/api/appointments/${consultationId}/notes`)
        .then(r => r.json())
        .then(notes => {
            document.getElementById('editQueixa').value = notes.queixa?.content || '';
            document.getElementById('editQueixaId').value = notes.queixa?.id || '';
            
            document.getElementById('editAnamnese').value = notes.anamnese?.content || '';
            document.getElementById('editAnamneseId').value = notes.anamnese?.id || '';
            
            document.getElementById('editDiagnostico').value = notes.diagnostico?.content || '';
            document.getElementById('editDiagnosticoId').value = notes.diagnostico?.id || '';
            
            document.getElementById('editConduta').value = notes.conduta?.content || '';
            document.getElementById('editCondutaId').value = notes.conduta?.id || '';
            
            new bootstrap.Modal(document.getElementById('editConsultationModal')).show();
        })
        .catch(err => {
            console.error('Erro ao carregar notas:', err);
            new bootstrap.Modal(document.getElementById('editConsultationModal')).show();
        });
}

// Salvar edição da consulta
function saveConsultationEdit() {
    const consultationId = document.getElementById('editConsultationId').value;
    const dateTime = document.getElementById('editConsultationDateTime').value;
    
    if (!dateTime) {
        showAlert('Por favor, selecione uma data e hora', 'warning');
        return;
    }
    
    // Array de promessas para atualizar cada nota
    const updatePromises = [];
    
    // Atualizar data da consulta - calcular end_time (1 hora depois por padrão)
    const start = new Date(dateTime);
    const end = new Date(start.getTime() + 60 * 60 * 1000);
    
    updatePromises.push(
        fetch(`/api/appointments/${consultationId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                start: dateTime,
                end: end.toISOString().slice(0, 16).replace('T', ' ')
            })
        })
    );
    
    // Atualizar cada nota individualmente
    const fields = ['Queixa', 'Anamnese', 'Diagnostico', 'Conduta'];
    fields.forEach(field => {
        const noteId = document.getElementById(`edit${field}Id`).value;
        const content = document.getElementById(`edit${field}`).value;
        
        if (noteId) {
            updatePromises.push(
                fetch(`/api/notes/${noteId}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({content: content})
                })
            );
        }
    });
    
    // Esperar todas as atualizações
    Promise.all(updatePromises)
        .then(responses => Promise.all(responses.map(r => r.json())))
        .then(results => {
            if (results.every(r => r.success)) {
                showAlert('Consulta atualizada com sucesso!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('editConsultationModal')).hide();
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showAlert('Erro ao atualizar algumas informações', 'danger');
            }
        })
        .catch(err => {
            console.error('Erro:', err);
            showAlert('Erro ao atualizar consulta', 'danger');
        });
}

// Deletar consulta
function deleteConsultation(consultationId, dateStr) {
    if (!confirm(`Tem certeza que deseja deletar a consulta de ${dateStr}?\n\nEsta ação não pode ser desfeita.`)) {
        return;
    }
    
    fetch(`/api/appointments/${consultationId}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Consulta deletada com sucesso!', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showAlert(result.error || 'Erro ao deletar', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao deletar consulta', 'danger');
    });
}

// ============ EVOLUTION FUNCTIONS ============
function openEvolutionModal() {
    const now = new Date();
    document.getElementById('evolutionDate').value = now.toISOString().slice(0, 16);
    document.getElementById('evolutionContent').value = '';
    document.getElementById('evolutionConsultation').value = '';
    loadConsultationsDropdown();
    new bootstrap.Modal(document.getElementById('evolutionModal')).show();
}

function loadConsultationsDropdown() {
    fetch(`/api/patient/${patientId}/consultations`)
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById('evolutionConsultation');
            select.innerHTML = '<option value="">-- Selecione uma consulta --</option>';
            (data.consultations || []).forEach(consultation => {
                const option = document.createElement('option');
                option.value = consultation.id;
                option.textContent = `${consultation.date} - ${consultation.category || 'Consulta'}`;
                select.appendChild(option);
            });
        })
        .catch(err => console.error('Erro ao carregar consultas:', err));
}

function saveEvolution() {
    const content = document.getElementById('evolutionContent').value.trim();
    const date = document.getElementById('evolutionDate').value;
    const modal = document.getElementById('evolutionModal');
    const surgeryId = modal.dataset.surgeryId;
    const type = modal.dataset.type;
    const patId = window.patientId || patientId;
    
    if (!content) {
        showAlert('Descrição vazia!', 'warning');
        return;
    }
    
    console.log('saveEvolution - type:', type, 'surgeryId:', surgeryId);
    
    if (type === 'surgery' && surgeryId) {
        // Salvar evolução de cirurgia
        fetch(`/api/patient/${patId}/surgery/${surgeryId}/evolution`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ content: content })
        })
        .then(r => r.json())
        .then(result => {
            console.log('Resultado evolução cirurgia:', result);
            if (result.success) {
                showAlert('✅ Evolução de cirurgia salva!', 'success');
                bootstrap.Modal.getInstance(modal).hide();
                loadTimeline();
            } else {
                showAlert(result.error || 'Erro ao salvar', 'danger');
            }
        })
        .catch(err => {
            console.error('Erro:', err);
            showAlert('Erro ao salvar evolução', 'danger');
        });
    } else {
        // Salvar evolução de consulta
        let consultationId = modal.dataset.consultationId || document.getElementById('evolutionConsultation').value;
        
        if (!consultationId || consultationId === '' || consultationId === undefined) {
            showAlert('Selecione uma consulta!', 'warning');
            return;
        }
        
        // Garantir que é um número válido
        consultationId = parseInt(String(consultationId).trim());
        
        if (isNaN(consultationId)) {
            showAlert('ID de consulta inválido!', 'warning');
            return;
        }
        
        console.log('Salvando evolução consulta - consultationId:', consultationId, 'from dataset:', modal.dataset.consultationId);
        
        fetch(`/api/patient/${patId}/evolution`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                content: content,
                evolution_date: date,
                consultation_id: consultationId
            })
        })
        .then(r => r.json())
        .then(result => {
            console.log('Resultado evolução consulta:', result);
            if (result.success) {
                showAlert('Evolução salva com sucesso!', 'success');
                bootstrap.Modal.getInstance(modal).hide();
                loadTimeline();
            } else {
                showAlert(result.error || 'Erro ao salvar', 'danger');
            }
        })
        .catch(err => {
            console.error('Erro ao salvar evolução:', err);
            showAlert('Erro ao salvar evolução: ' + err.message, 'danger');
        });
    }
}


function calculateDaysPassed(dateStr) {
    // Parse data no formato DD/MM/YYYY
    const [day, month, year] = dateStr.split('/').map(Number);
    const surgeryDate = new Date(year, month - 1, day);
    const today = new Date();
    
    const diffTime = today - surgeryDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    // Calcular anos, meses e dias
    let years = Math.floor(diffDays / 365);
    let months = Math.floor((diffDays % 365) / 30);
    let days = diffDays % 30;
    
    // Formatar output
    const parts = [];
    if (years > 0) parts.push(`${years} ano${years !== 1 ? 's' : ''}`);
    if (months > 0) parts.push(`${months} mês${months !== 1 ? 'es' : ''}`);
    if (days > 0 || parts.length === 0) parts.push(`${days} dia${days !== 1 ? 's' : ''}`);
    
    return parts.slice(0, 2).join(' e '); // Mostrar no máximo 2 unidades
}

function groupSurgeriesByMonthYear(surgeries) {
    const grouped = {};
    
    surgeries.forEach(surgery => {
        const [day, month, year] = surgery.surgery_date.split('/');
        const key = `${month}/${year}`;
        const monthYear = new Date(year, month - 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
        
        if (!grouped[key]) {
            grouped[key] = { monthYear, surgeries: [] };
        }
        grouped[key].surgeries.push(surgery);
    });
    
    return grouped;
}

function renderSurgeries(surgeries = []) {
    const container = document.getElementById('surgeriesContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (surgeries.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">Nenhuma cirurgia registrada.</p>';
        return;
    }
    
    // Agrupar cirurgias por mês/ano
    const grouped = groupSurgeriesByMonthYear(surgeries);
    
    // Renderizar grupos
    Object.keys(grouped).sort().reverse().forEach(key => {
        const group = grouped[key];
        
        // Criar header do grupo
        const groupHeader = document.createElement('div');
        groupHeader.className = 'mb-3 mt-3 pt-2 border-top';
        groupHeader.innerHTML = `<h6 class="text-secondary text-capitalize">${group.monthYear}</h6>`;
        container.appendChild(groupHeader);
        
        // Renderizar cirurgias do grupo
        group.surgeries.forEach(surgery => {
            const daysPassed = calculateDaysPassed(surgery.surgery_date);
            
            const surgeryDiv = document.createElement('div');
            surgeryDiv.className = 'mb-4 p-3 border rounded';
            surgeryDiv.style.backgroundColor = '#e3f2fd';
            surgeryDiv.style.borderLeft = '5px solid #2196F3';
            
            surgeryDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h6 class="mb-1"><i class="bi bi-heart-pulse"></i> <strong>${surgery.surgery_date}</strong></h6>
                        <p class="mb-1"><small class="text-success"><i class="bi bi-hourglass-split"></i> ${daysPassed}</small></p>
                        <p class="mb-1"><small><strong>Cirurgia de Transplante</strong></small></p>
                    </div>
                    <button class="btn btn-sm btn-outline-success" onclick="openSurgeryEvolutionModal(${surgery.id}, '${surgery.surgery_date}')">
                        <i class="bi bi-plus"></i> Evolução
                    </button>
                </div>
                <p style="white-space: pre-wrap;"><strong>Dados:</strong> ${surgery.surgical_data}</p>
                ${surgery.observations ? `<p><strong>Observações:</strong> ${surgery.observations}</p>` : ''}
                <p class="mb-3"><small class="text-muted">Dr. ${surgery.doctor_name}</small></p>
            `;
            
            // Sempre adicionar seção de evoluções da cirurgia
            const evolutionsDiv = document.createElement('div');
            evolutionsDiv.className = 'mt-3 pt-3 border-top';
            
            const evoHeader = document.createElement('h6');
            evoHeader.className = 'text-success mb-2';
            evoHeader.innerHTML = '<i class="bi bi-stickies"></i> Evoluções';
            evolutionsDiv.appendChild(evoHeader);
            
            if (surgery.evolutions && surgery.evolutions.length > 0) {
                const evosContainer = document.createElement('div');
                evosContainer.className = 'ms-2 ps-3 border-start border-success';
                
                surgery.evolutions.forEach(evo => {
                    const evoDiv = document.createElement('div');
                    evoDiv.className = 'mb-3 p-2 bg-light rounded';
                    evoDiv.style.borderLeft = '4px solid #198754';
                    
                    evoDiv.innerHTML = `
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <small class="text-muted"><i class="bi bi-clock"></i> ${evo.date}</small>
                                <p class="mb-1 mt-2" style="white-space: pre-wrap;">${evo.content}</p>
                                <small class="text-muted">Dr. ${evo.doctor}</small>
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
                const noEvo = document.createElement('p');
                noEvo.className = 'text-muted small mb-0';
                noEvo.innerHTML = '<em>Nenhuma evolução registrada</em>';
                evolutionsDiv.appendChild(noEvo);
            }
            
            surgeryDiv.appendChild(evolutionsDiv);
            
            container.appendChild(surgeryDiv);
        });
    });
}

function renderEvolutionsInAccordion(consultations = []) {
    const timelineContainer = document.getElementById('consultationTimelineList');
    if (!timelineContainer) return;

    window.timelineConsultations = consultations || [];

    if (!consultations || consultations.length === 0) {
        timelineContainer.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-4"></i>
                <p class="mb-0 mt-2">Nenhuma consulta registrada para este paciente.</p>
            </div>
        `;
        return;
    }

    const escapeHtml = (value) => String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');

    const buildEvolutionItem = (evo) => `
        <div class="timeline-evolution-item">
            <div class="d-flex justify-content-between align-items-start gap-2">
                <div>
                    <div class="small text-muted mb-1"><i class="bi bi-clock"></i> ${evo.date} • Dr. ${evo.doctor}</div>
                    <div class="timeline-evolution-text">${escapeHtml(evo.content)}</div>
                </div>
                <div class="d-flex gap-1 flex-shrink-0">
                    <button class="btn btn-sm btn-outline-warning" title="Editar evolução" data-content="${escapeHtml(evo.content)}" onclick="editEvolution(${evo.id}, this)">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" title="Excluir evolução" onclick="deleteEvolution(${evo.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;

    const buildQuickAdd = (consultation) => `
        <div class="timeline-quick-add mt-2">
            <textarea class="form-control form-control-sm" id="quickEvolution-${consultation.id}" rows="2" placeholder="Adicionar nova evolução..."></textarea>
            <div class="d-flex justify-content-end mt-2">
                <button class="btn btn-sm btn-success" onclick="saveQuickEvolution(${consultation.id})">
                    <i class="bi bi-plus-circle"></i> Adicionar Evolução
                </button>
            </div>
        </div>
    `;

    const timelineHtml = consultations.map((consultation, index) => {
        const isCurrent = index === 0;
        const evolutionsHtml = consultation.evolutions && consultation.evolutions.length > 0
            ? consultation.evolutions.map(buildEvolutionItem).join('')
            : `<div class="timeline-evolution-empty">Nenhuma evolução registrada.</div>`;

        return `
            <div class="timeline-entry ${isCurrent ? 'timeline-entry-current' : ''}">
                <div class="timeline-dot ${isCurrent ? 'timeline-dot-current' : ''}"></div>
                <div class="timeline-content">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
                        <div>
                            <h6 class="mb-1">${isCurrent ? '🔽 Atendimento Atual' : '⚫ Histórico'} • ${consultation.date}</h6>
                            <div class="small text-muted">
                                <span class="badge bg-primary">${consultation.category || 'Consulta'}</span>
                                <span class="ms-2"><i class="bi bi-person-circle"></i> ${consultation.doctor_name || 'N/A'}</span>
                                ${consultation.status !== 'atendido' ? '<span class="badge bg-secondary ms-2">Rascunho</span>' : ''}
                            </div>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-outline-success" onclick="openEvolutionFromConsultation(${consultation.id}, '${consultation.date}')">
                                <i class="bi bi-plus-circle"></i> Evolução
                            </button>
                        </div>
                    </div>
                    <div class="timeline-evolution-list">${evolutionsHtml}</div>
                    ${buildQuickAdd(consultation)}
                </div>
            </div>
        `;
    }).join('');

    timelineContainer.innerHTML = `<div class="timeline-track">${timelineHtml}</div>`;
}

function saveQuickEvolution(consultationId) {
    const input = document.getElementById(`quickEvolution-${consultationId}`);
    if (!input) return;
    const content = input.value.trim();
    if (!content) {
        showAlert('Digite o conteúdo da evolução.', 'warning');
        return;
    }

    const id = window.patientId || patientId;
    fetch(`/api/patient/${id}/evolution`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ content, consultation_id: consultationId })
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            input.value = '';
            showAlert('Evolução adicionada na linha do tempo!', 'success');
            loadTimeline();
        } else {
            showAlert(result.error || 'Erro ao salvar evolução', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao salvar evolução', 'danger');
    });
}

function editEvolution(evoId, buttonEl) {
    const currentContent = buttonEl ? (buttonEl.dataset.content || '') : '';
    const updatedContent = prompt('Editar evolução:', currentContent);
    if (updatedContent === null) return;
    if (!updatedContent.trim()) {
        showAlert('Conteúdo não pode ficar vazio.', 'warning');
        return;
    }

    fetch(`/api/evolution/${evoId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ content: updatedContent.trim() })
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Evolução atualizada com sucesso!', 'success');
            loadTimeline();
        } else {
            showAlert(result.error || 'Erro ao atualizar evolução', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao atualizar evolução', 'danger');
    });
}

function openSurgeryEvolutionModal(surgeryId, surgeryDate) {
    const modal = document.getElementById('evolutionModal');
    document.getElementById('evolutionDate').value = new Date().toISOString().slice(0, 16);
    document.getElementById('evolutionContent').value = '';
    document.getElementById('evolutionConsultation').style.display = 'none';
    document.getElementById('evolutionConsultationDisplay').style.display = 'block';
    document.getElementById('evolutionConsultationName').textContent = `🏥 Cirurgia de ${surgeryDate}`;
    
    modal.dataset.surgeryId = surgeryId;
    modal.dataset.fromConsultation = 'false';
    modal.dataset.type = 'surgery';
    
    new bootstrap.Modal(modal).show();
}

function deleteSurgeryEvolution(evolutionId) {
    if (!confirm('Tem certeza que deseja deletar esta evolução da cirurgia?')) return;
    
    fetch(`/api/patient/surgery-evolution/${evolutionId}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('✅ Evolução deletada!', 'success');
            loadTimeline();
        } else {
            showAlert(result.error || 'Erro ao deletar', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao deletar evolução', 'danger');
    });
}

function openEvolutionFromConsultation(consultationId, consultationDate) {
    console.log('openEvolutionFromConsultation - consultationId:', consultationId);
    
    // Tentar encontrar o collapse correspondente no histórico (Timeline)
    var collapseId = 'collapse' + consultationId;
    var collapseEl = document.getElementById(collapseId);
    
    if (collapseEl) {
        // Se encontrou o elemento no histórico, apenas rola até ele e abre
        collapseEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        var bsCollapse = new bootstrap.Collapse(collapseEl, { toggle: false });
        bsCollapse.show();
        
        // Pequeno destaque visual
        var content = collapseEl.querySelector('.timeline-content');
        if (content) {
            content.style.backgroundColor = '#fff3cd';
            setTimeout(function() { content.style.backgroundColor = ''; }, 2000);
        }
        return;
    }

    // Se NÃO encontrou no histórico (Timeline), abre o modal de nova evolução
    var consultations = window.timelineConsultations || [];
    var consultation = null;
    for (var i = 0; i < consultations.length; i++) {
        if (String(consultations[i].id) === String(consultationId)) {
            consultation = consultations[i];
            break;
        }
    }
    
    var category = consultation ? consultation.category : 'Consulta';
    var displayDate = consultation ? consultation.date : consultationDate;
    var isSurgery = category && category.toLowerCase().indexOf('cirurgia') !== -1;
    var surgeryDateOnly = displayDate ? displayDate.split(' ')[0] : null;

    var modalHtml = '<div class="modal fade" id="evolutionModal" tabindex="-1">' +
        '<div class="modal-dialog modal-lg">' +
            '<div class="modal-content">' +
                '<div class="modal-header bg-success text-white">' +
                    '<h5 class="modal-title"><i class="bi bi-plus-circle"></i> Nova Evolução</h5>' +
                    '<button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>' +
                '</div>' +
                '<div class="modal-body">' +
                    '<div class="alert alert-success d-flex align-items-center mb-3">' +
                        '<i class="bi bi-calendar-event me-2"></i>' +
                        '<div><strong>' + category + ' de ' + displayDate + '</strong></div>' +
                    '</div>' +
                    '<div class="mb-3">' +
                        '<label class="form-label fw-bold">Data da Evolução</label>' +
                        '<input type="datetime-local" class="form-control" id="evolution_date_manual">' +
                    '</div>' +
                    (isSurgery ? 
                    '<div class="mb-4">' +
                        '<label class="form-label fw-bold">Tipo de Evolução Pós-Cirúrgica:</label>' +
                        '<div class="btn-group w-100" role="group">' +
                            '<input type="radio" class="btn-check" name="evolution_type_manual" id="evo_rotina_m" value="general" checked>' +
                            '<label class="btn btn-outline-secondary" for="evo_rotina_m"><i class="bi bi-journal-text"></i> Rotina</label>' +
                            '<input type="radio" class="btn-check" name="evolution_type_manual" id="evo_7dias_m" value="7_days">' +
                            '<label class="btn btn-outline-warning" for="evo_7dias_m"><i class="bi bi-calendar-week"></i> 7 Dias</label>' +
                            '<input type="radio" class="btn-check" name="evolution_type_manual" id="evo_1ano_m" value="1_year">' +
                            '<label class="btn btn-outline-info" for="evo_1ano_m"><i class="bi bi-calendar-check"></i> 1 Ano</label>' +
                        '</div>' +
                    '</div>' : '') +
                    '<div id="evolutionFormContainerManual">' +
                        '<div class="mb-3">' +
                            '<label class="form-label fw-bold">Descrição</label>' +
                            '<textarea class="form-control" id="evolution_content_manual" rows="6" placeholder="Descreva a evolução do paciente..."></textarea>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
                '<div class="modal-footer">' +
                    '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>' +
                    '<button type="button" class="btn btn-success" id="btnSaveEvolutionManual"><i class="bi bi-save"></i> Salvar</button>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '</div>';

    var existingModal = document.getElementById('evolutionModal');
    if (existingModal) existingModal.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    var now = new Date();
    var offset = now.getTimezoneOffset() * 60000;
    var localISOTime = (new Date(now - offset)).toISOString().slice(0, 16);
    document.getElementById('evolution_date_manual').value = localISOTime;

    var modalElement = document.getElementById('evolutionModal');
    var bsModal = new bootstrap.Modal(modalElement);
    bsModal.show();

    document.getElementById('btnSaveEvolutionManual').onclick = function() {
        var content = document.getElementById('evolution_content_manual').value;
        var date = document.getElementById('evolution_date_manual').value;
        
        if (!content) {
            alert('Por favor, descreva a evolução');
            return;
        }

        var surgeryId = null;
        if (isSurgery && typeof window.timelineSurgeries !== 'undefined') {
            var matchedSurgery = window.timelineSurgeries.find(function(s) { return s.surgery_date === surgeryDateOnly; });
            if (matchedSurgery) surgeryId = matchedSurgery.id;
        }

        var payload = {
            consultation_id: consultationId,
            content: content,
            evolution_date: date,
            evolution_type: isSurgery ? (document.querySelector('input[name="evolution_type_manual"]:checked')?.value || 'general') : 'general'
        };

        var endpoint = surgeryId ? ('/api/surgery/' + surgeryId + '/evolution') : ('/api/patient/' + (window.patientId || '') + '/evolution');

        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(function(r) { return r.json(); })
        .then(function(res) {
            if (res.success) {
                bsModal.hide();
                location.reload();
            } else {
                alert('Erro ao salvar: ' + (res.error || 'Erro desconhecido'));
            }
        });
    };
}

function openEvolutionModal() {
    // Limpar modal quando aberto sem consulta específica
    const modal = document.getElementById('evolutionModal');
    const now = new Date();
    
    document.getElementById('evolutionDate').value = now.toISOString().slice(0, 16);
    document.getElementById('evolutionContent').value = '';
    document.getElementById('evolutionConsultation').value = '';
    
    document.getElementById('evolutionConsultation').style.display = 'block';
    document.getElementById('evolutionConsultationDisplay').style.display = 'none';
    
    modal.dataset.fromConsultation = 'false';
    modal.dataset.type = 'consultation';
    delete modal.dataset.surgeryId;
    delete modal.dataset.consultationId;
    
    loadConsultationsDropdown();
    new bootstrap.Modal(modal).show();
}

function deleteEvolution(evoId) {
    if (!confirm('Tem certeza que deseja deletar esta evolução?')) return;
    
    fetch(`/api/evolution/${evoId}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Evolução deletada!', 'success');
            loadTimeline();
        } else {
            showAlert(result.error || 'Erro ao deletar', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao deletar evolução', 'danger');
    });
}

function renderTimeline(consultations = [], surgeries = []) {
    console.log('renderTimeline - consultations:', consultations, 'surgeries:', surgeries);
    renderEvolutionsInAccordion(consultations || []);
    renderSurgeries(surgeries || []);
}

function loadTimeline() {
    const id = window.patientId || patientId;
    if (!id) {
        console.error('patientId não encontrado');
        return;
    }
    
    // Carregar consultas E cirurgias da API
    Promise.all([
        fetch(`/api/patient/${id}/evolutions`).then(r => r.json()),
        fetch(`/api/patient/${id}/surgeries`).then(r => r.json())
    ])
    .then(([consultations, surgeries]) => {
        renderTimeline(consultations || [], surgeries || []);
    })
    .catch(err => console.error('Erro ao carregar timeline:', err));
}

// Carregar timeline ao abrir a página
document.addEventListener('DOMContentLoaded', function() {
    loadTimeline();
});

function openEditPatientModal() {
    const modal = new bootstrap.Modal(document.getElementById('editPatientModal'));
    modal.show();
}

function savePatientData() {
    const data = {
        name: document.getElementById('editPatientName').value,
        email: document.getElementById('editPatientEmail').value,
        phone: document.getElementById('editPatientPhone').value,
        birth_date: document.getElementById('editPatientBirthDate').value,
        cpf: document.getElementById('editPatientCpf').value,
        address: document.getElementById('editPatientAddress').value,
        city: document.getElementById('editPatientCity').value,
        state: document.getElementById('editPatientState').value,
        zip_code: document.getElementById('editPatientZip').value
    };
    
    if (!data.name) {
        showAlert('Nome é obrigatório', 'danger');
        return;
    }
    
    const id = window.patientId || patientId;
    
    fetch(`/api/patient/${id}/update`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Dados atualizados com sucesso!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editPatientModal')).hide();
            setTimeout(() => location.reload(), 500);
        } else {
            showAlert(result.error || 'Erro ao atualizar', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao salvar dados', 'danger');
    });
}

function saveTransplantIndication() {
    const indication = document.querySelector('input[name="transplantIndication"]:checked')?.value;
    if (!indication) return;
    
    const id = window.patientId || patientId;
    
    fetch(`/api/patient/${id}/transplant-indication`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({has_indication: indication === 'sim'})
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Indicação salva!', 'success');
        } else {
            showAlert(result.error || 'Erro ao salvar', 'danger');
        }
    })
    .catch(err => console.error('Erro:', err));
}

function abrirDermaScribe() {
    let patientName = '';
    
    const h2Element = document.querySelector('h2');
    if (h2Element) {
        patientName = h2Element.textContent.replace('Prontuário:', '').trim();
    }
    
    if (!patientName) {
        patientName = document.getElementById('patientName')?.textContent?.trim() || 
                      document.querySelector('.patient-name')?.textContent?.trim() || 
                      window.patientName || '';
    }
    
    const cleanName = patientName.replace(/\s*\(\d+\s*anos?\)/gi, '').replace(/Editar\s*Cadastro/gi, '').trim();
    const encodedName = encodeURIComponent(cleanName);
    const currentPatientId = window.patientId || patientId;
    const dermaScribeUrl = `/dermascribe/?patient=${encodedName}&patient_id=${currentPatientId}`;
    
    window.dermaScribeWindow = window.open(dermaScribeUrl, 'DermaScribe', 'width=1200,height=900,scrollbars=yes,resizable=yes');
}

function handleDermaScribeMessage(event) {
    const data = event.data;
    if (data && data.type === 'prescription_saved') {
        showAlert('Receita salva com sucesso no prontuário!', 'success');
    }
}

function savePrescriptionToConduta(prescriptionData) {
    const patientId = window.patientId || document.getElementById('patientId')?.value;
    if (!patientId) {
        console.error('Patient ID não encontrado');
        return;
    }
    
    fetch(`/api/patient/${patientId}/prescription`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(prescriptionData)
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Receita salva na conduta!', 'success');
            loadPrescriptionHistory();
            const condutaText = document.getElementById('condutaText');
            if (condutaText && prescriptionData.summary) {
                const currentText = condutaText.value;
                const separator = currentText ? '\n\n' : '';
                condutaText.value = currentText + separator + '📋 RECEITA: ' + prescriptionData.summary;
            }
        } else {
            showAlert(result.error || 'Erro ao salvar receita', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro ao salvar receita:', err);
        showAlert('Erro ao salvar receita', 'danger');
    });
}

function loadPrescriptionHistory() {
    const currentPatientId = window.patientId || patientId;
    if (!currentPatientId) return;
    
    fetch(`/dermascribe/api/patient/${currentPatientId}/prescriptions`)
    .then(r => r.json())
    .then(data => {
        const container = document.getElementById('prescriptionHistoryList');
        if (!container) return;
        
        if (!data.prescriptions || data.prescriptions.length === 0) {
            container.innerHTML = '<small class="text-muted">Nenhuma receita emitida</small>';
            return;
        }
        
        let html = '<ul class="list-unstyled mb-0">';
        data.prescriptions.forEach(p => {
            let summary = '';
            if (p.oral && p.oral.length > 0) {
                summary += `Oral: ${p.oral.map(m => m.medication || m).join(', ')}. `;
            }
            if (p.topical && p.topical.length > 0) {
                summary += `Tópico: ${p.topical.map(m => m.medication || m).join(', ')}`;
            }
            
            html += `<li class="mb-2 p-2 bg-light rounded">
                <small class="text-muted">${p.created_at} - Dr(a). ${p.doctor}</small>
                <div class="small">${summary || 'Receita'}</div>
                <button class="btn btn-sm btn-outline-primary mt-1" onclick="printPrescription(${p.id})">
                    <i class="bi bi-printer"></i> Imprimir
                </button>
            </li>`;
        });
        html += '</ul>';
        container.innerHTML = html;
    })
    .catch(err => console.error('Erro ao carregar histórico:', err));
}

function printPrescription(prescriptionId) {
    window.open(`/dermascribe/prescription/${prescriptionId}/print`, '_blank');
}

function viewPrescription(prescriptionId) {
    window.open(`/prescription/${prescriptionId}/print`, '_blank');
}
