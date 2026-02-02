// ========== GERENCIAR CIRURGIAS ==========

// Tornar as funcoes globais anexando ao objeto window explicitamente
window.saveSurgery = function() {
    console.log('saveSurgery chamada');
    
    // Tentar pegar patientId de varias fontes
    const pId = typeof patientId !== 'undefined' ? patientId : (document.getElementById('detailPatientId')?.value || null);
    
    if (!pId) {
        console.error('patientId nao encontrado!');
        if (typeof showAlert === 'function') {
            showAlert('Erro: ID do paciente nao encontrado.', 'danger');
        } else {
            alert('Erro: ID do paciente nao encontrado.');
        }
        return;
    }

    // IDs dos campos podem variar entre a aba "Cirurgias" e o modal de "Planejamento"
    const surgeryDate = document.getElementById('surgeryDate')?.value || document.getElementById('surgeryModalDate')?.value;
    const surgicalData = (document.getElementById('surgicalData')?.value || document.getElementById('surgeryModalSurgicalPlanning')?.value || '').trim();
    const observations = (document.getElementById('surgeryObservations')?.value || document.getElementById('surgeryModalComplications')?.value || '').trim();
    
    if (!surgeryDate) {
        if (typeof showAlert === 'function') showAlert('Selecione a data da cirurgia!', 'warning');
        return;
    }
    
    if (!surgicalData) {
        if (typeof showAlert === 'function') showAlert('Preencha os dados cirurgicos!', 'warning');
        return;
    }
    
    fetch(`/api/patient/${pId}/surgery`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', 
            'X-CSRFToken': typeof getCSRFToken === 'function' ? getCSRFToken() : ''
        },
        body: JSON.stringify({
            surgery_date: surgeryDate.split('T')[0], // Garantir apenas data YYYY-MM-DD
            surgical_data: surgicalData,
            observations: observations
        })
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            if (typeof showAlert === 'function') showAlert('Cirurgia registrada com sucesso!', 'success');
            // Limpar campos de ambos os formularios
            ['surgeryDate', 'surgicalData', 'surgeryObservations', 'surgeryModalDate', 'surgeryModalSurgicalPlanning', 'surgeryModalComplications'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });
            
            // Fechar modal se aberto
            const modalEl = document.getElementById('surgeryModal');
            if (modalEl) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }
            
            if (typeof loadSurgeries === 'function') loadSurgeries();
        } else {
            if (typeof showAlert === 'function') showAlert('Erro: ' + (result.error || 'Erro ao salvar'), 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        if (typeof showAlert === 'function') showAlert('Erro ao salvar cirurgia', 'danger');
    });
};

window.loadSurgeries = function() {
    console.log('loadSurgeries chamada');
    // Forçar busca do patientId se necessário
    const pId = typeof patientId !== 'undefined' ? patientId : (document.getElementById('detailPatientId')?.value || null);
    if (!pId) {
        console.warn('loadSurgeries: pId nao encontrado');
        return;
    }
    
    fetch(`/api/patient/${pId}/surgeries`)
        .then(r => r.json())
        .then(surgeries => {
            console.log('Cirurgias carregadas:', surgeries);
            renderSurgeries(surgeries);
        })
        .catch(err => console.error('Erro ao carregar cirurgias:', err));
};

window.deleteSurgery = function(surgeryId) {
    if (!confirm('Tem certeza que deseja deletar esta cirurgia?')) return;
    
    fetch(`/api/patient/delete/${surgeryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': typeof getCSRFToken === 'function' ? getCSRFToken() : ''
        }
    })
    .then(r => {
        if (!r.ok) throw new Error('Falha na resposta do servidor');
        return r.json();
    })
    .then(result => {
        if (result.success) {
            if (typeof showAlert === 'function') showAlert('Cirurgia deletada!', 'success');
            window.loadSurgeries();
        } else {
            if (typeof showAlert === 'function') showAlert('Erro: ' + (result.error || 'Erro ao deletar'), 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        if (typeof showAlert === 'function') showAlert('Erro ao deletar cirurgia', 'danger');
    });
};

window.createEvolutionForSurgery = createEvolutionForSurgery;
window.viewEvolutions = viewEvolutions;

// Função para calcular tempo desde cirurgia
function calculateSurgeryTime(surgeryDate) {
    try {
        // Se receber string dd/mm/yyyy, converter para YYYY-MM-DD
        let dateStr = surgeryDate;
        if (surgeryDate.includes('/')) {
            const parts = surgeryDate.split('/');
            dateStr = `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        
        // Parse em UTC para evitar problemas de timezone
        const [year, month, day] = dateStr.split('-').map(Number);
        const surgery = new Date(Date.UTC(year, month - 1, day));
        const today = new Date();
        
        let years = today.getFullYear() - surgery.getFullYear();
        let months = today.getMonth() - surgery.getMonth();
        let days = today.getDate() - surgery.getDate();
        
        if (days < 0) {
            months--;
            days += 30;
        }
        if (months < 0) {
            years--;
            months += 12;
        }
        
        let timeStr = `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')}/${year}`;
        let timePassed = [];
        
        if (years > 0) timePassed.push(`${years} ano${years > 1 ? 's' : ''}`);
        if (months > 0) timePassed.push(`${months} mês${months > 1 ? 'es' : ''}`);
        if (days > 0 && years === 0 && months < 3) timePassed.push(`${days} dia${days > 1 ? 's' : ''}`);
        
        return `${timeStr} - ${timePassed.length > 0 ? timePassed.join(' e ') + ' desde cirurgia' : 'Cirurgia recente'}`;
    } catch (e) {
        console.error('Erro ao calcular data:', e, surgeryDate);
        return 'Data inválida';
    }
}

function renderSurgeries(surgeries) {
    const container = document.getElementById('surgeriesList');
    if (!container) return;
    
    if (!surgeries || surgeries.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><em>Nenhuma cirurgia registrada</em></div>';
        return;
    }
    
    const sorted = [...surgeries].sort((a, b) => new Date(b.surgery_date) - new Date(a.surgery_date));
    
    container.innerHTML = sorted.map((surgery, idx) => {
        const daysSince = calculateDaysSince(surgery.surgery_date);
        let evolutionBtnClass = 'btn-success';
        let evolutionBtnText = '<i class="bi bi-plus-circle"></i> Evolução';
        
        if (daysSince >= 365) {
            evolutionBtnClass = 'btn-info';
            evolutionBtnText = '<i class="bi bi-star"></i> Resultado 1 Ano';
        } else if (daysSince >= 7) {
            evolutionBtnClass = 'btn-warning';
            evolutionBtnText = '<i class="bi bi-clipboard-pulse"></i> Evolução 7 Dias';
        }
        
        return `
        <div class="card mb-3 border-left border-success" style="border-left: 5px solid #198754;">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h6 class="mb-2 text-success">
                            <i class="bi bi-calendar2-check"></i> 
                            <strong>${calculateSurgeryTime(surgery.surgery_date)}</strong>
                        </h6>
                        
                        <div class="mb-2">
                            <strong>Dados Cirúrgicos:</strong>
                            <p class="mb-0 p-2 bg-light rounded" style="white-space: pre-wrap; font-size: 0.9rem;">
                                ${surgery.surgical_data}
                            </p>
                        </div>
                        
                        ${surgery.observations ? `
                        <div class="mb-2">
                            <strong>Observações:</strong>
                            <p class="mb-0 p-2 bg-light rounded" style="white-space: pre-wrap; font-size: 0.9rem;">
                                ${surgery.observations}
                            </p>
                        </div>
                        ` : ''}
                        
                        <small class="text-muted"><i class="bi bi-person-fill"></i> Dr. ${surgery.doctor_name}</small>
                        
                        <div id="evolutions-${surgery.id}" class="mt-2"></div>
                    </div>
                    <div class="col-md-4">
                        <button class="btn btn-sm ${evolutionBtnClass} w-100 mb-2" onclick="createEvolutionForSurgery(${surgery.id}, '${surgery.surgery_date}')">
                            ${evolutionBtnText}
                        </button>
                        <button class="btn btn-sm btn-outline-secondary w-100 mb-2" onclick="viewEvolutions(${surgery.id})">
                            <i class="bi bi-list-check"></i> Ver Evoluções
                        </button>
                        <button class="btn btn-sm btn-outline-danger w-100" onclick="deleteSurgery(${surgery.id})">
                            <i class="bi bi-trash"></i> Deletar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `}).join('');
}

function viewEvolutions(surgeryId) {
    fetch(`/api/surgery/${surgeryId}/evolutions`)
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById(`evolutions-${surgeryId}`);
            if (!container) return;
            if (!data.evolutions || data.evolutions.length === 0) {
                container.innerHTML = '<div class="alert alert-secondary py-1 px-2 mb-0"><small>Nenhuma evolução registrada</small></div>';
                return;
            }
            
            container.innerHTML = `
                <div class="border rounded p-2 bg-light">
                    <strong class="d-block mb-2"><i class="bi bi-clipboard-data"></i> Evoluções (${data.evolutions.length})</strong>
                    ${data.evolutions.map(e => {
                        let badges = '';
                        if (e.evolution_type === '7_days') {
                            if (e.has_necrosis) badges += '<span class="badge bg-danger me-1">Necrose</span>';
                            if (e.has_infection) badges += '<span class="badge bg-danger me-1">Infecção</span>';
                            if (e.has_scabs) badges += '<span class="badge bg-warning text-dark me-1">Crostas</span>';
                            if (e.has_follicle_loss) badges += '<span class="badge bg-secondary me-1">Perda Folículos</span>';
                        } else if (e.evolution_type === '1_year') {
                            const resultColors = {otimo: 'success', bom: 'primary', medio: 'warning', ruim: 'danger'};
                            if (e.result_rating) badges += \`<span class="badge bg-\${resultColors[e.result_rating] || 'secondary'} me-1">\${e.result_rating.charAt(0).toUpperCase() + e.result_rating.slice(1)}</span>\`;
                            if (e.needs_another_surgery) badges += '<span class="badge bg-info me-1">Nova Cirurgia</span>';
                        }
                        
                        const date = new Date(e.evolution_date).toLocaleDateString('pt-BR');
                        return \`
                            <div class="border-bottom pb-2 mb-2">
                                <small class="text-muted">\${date} - Dr. \${e.doctor_name}</small>
                                <div>\${badges || ''}</div>
                                \${e.content ? \`<p class="mb-0 small">\${e.content}</p>\` : ''}
                            </div>
                        \`;
                    }).join('')}
                </div>
            `;
        })
        .catch(err => console.error('Erro ao carregar evoluções:', err));
}

function calculateDaysSince(surgeryDate) {
    let dateStr = surgeryDate;
    if (surgeryDate.includes('/')) {
        const parts = surgeryDate.split('/');
        dateStr = `${parts[2]}-${parts[1]}-${parts[0]}`;
    }
    const [year, month, day] = dateStr.split('-').map(Number);
    const surgery = new Date(Date.UTC(year, month - 1, day));
    const today = new Date();
    return Math.floor((today - surgery) / (1000 * 60 * 60 * 24));
}

function createEvolutionForSurgery(surgeryId, surgeryDate) {
    const daysSince = calculateDaysSince(surgeryDate);
    const modalHtml = `
        <div class="modal fade" id="surgeryEvolutionModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title"><i class="bi bi-clipboard-pulse"></i> Nova Evolução Pós-Cirúrgica</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-secondary mb-3">
                            <i class="bi bi-clock"></i> <strong>${daysSince} dias</strong> desde a cirurgia
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-bold">Tipo de Evolução:</label>
                            <div class="btn-group w-100" role="group">
                                <input type="radio" class="btn-check" name="evolution_type" id="evo_rotina" value="general" checked>
                                <label class="btn btn-outline-secondary" for="evo_rotina">Rotina</label>
                                <input type="radio" class="btn-check" name="evolution_type" id="evo_7dias" value="7_days">
                                <label class="btn btn-outline-warning" for="evo_7dias">7 Dias</label>
                                <input type="radio" class="btn-check" name="evolution_type" id="evo_1ano" value="1_year">
                                <label class="btn btn-outline-info" for="evo_1ano">1 Ano</label>
                            </div>
                        </div>
                        <div id="evolutionFormContainer"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-success" id="btnSaveEvolution">Salvar Evolução</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const existingModal = document.getElementById('surgeryEvolutionModal');
    if (existingModal) existingModal.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    document.getElementById('evolutionFormContainer').innerHTML = getEvolutionFormHtml('general');
    
    document.getElementById('btnSaveEvolution').addEventListener('click', function() {
        saveSurgeryEvolution(surgeryId);
    });
    
    document.querySelectorAll('input[name="evolution_type"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.getElementById('evolutionFormContainer').innerHTML = getEvolutionFormHtml(this.value);
        });
    });
    
    const modal = new bootstrap.Modal(document.getElementById('surgeryEvolutionModal'));
    modal.show();
}

function getEvolutionFormHtml(type) {
    if (type === '1_year') {
        return `
            <div class="mb-3">
                <label class="form-label fw-bold">Resultado:</label>
                <div class="btn-group w-100" role="group">
                    <input type="radio" class="btn-check" name="result_rating" id="result_otimo" value="otimo">
                    <label class="btn btn-outline-success" for="result_otimo">Ótimo</label>
                    <input type="radio" class="btn-check" name="result_rating" id="result_bom" value="bom">
                    <label class="btn btn-outline-primary" for="result_bom">Bom</label>
                    <input type="radio" class="btn-check" name="result_rating" id="result_medio" value="medio">
                    <label class="btn btn-outline-warning" for="result_medio">Médio</label>
                    <input type="radio" class="btn-check" name="result_rating" id="result_ruim" value="ruim">
                    <label class="btn btn-outline-danger" for="result_ruim">Ruim</label>
                </div>
            </div>
            <div class="mb-3">
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="needs_another_surgery">
                    <label class="form-check-label" for="needs_another_surgery">Indicação de nova cirurgia</label>
                </div>
            </div>
            <textarea class="form-control" id="evolution_content" rows="4" placeholder="Observações..."></textarea>
        `;
    } else if (type === '7_days') {
        return `
            <div class="row mb-3">
                <div class="col-6"><div class="form-check"><input class="form-check-input" type="checkbox" id="has_necrosis"><label class="form-check-label">Necrose</label></div></div>
                <div class="col-6"><div class="form-check"><input class="form-check-input" type="checkbox" id="has_scabs"><label class="form-check-label">Crostas</label></div></div>
                <div class="col-6"><div class="form-check"><input class="form-check-input" type="checkbox" id="has_infection"><label class="form-check-label">Infecção</label></div></div>
                <div class="col-6"><div class="form-check"><input class="form-check-input" type="checkbox" id="has_follicle_loss"><label class="form-check-label">Perda Folículos</label></div></div>
            </div>
            <textarea class="form-control" id="evolution_content" rows="4" placeholder="Observações..."></textarea>
        `;
    }
    return `<textarea class="form-control" id="evolution_content" rows="6" placeholder="Descrição da evolução..."></textarea>`;
}

function saveSurgeryEvolution(surgeryId) {
    const data = {
        content: document.getElementById('evolution_content')?.value || '',
        evolution_type: document.querySelector('input[name="evolution_type"]:checked')?.value || 'general',
        has_necrosis: document.getElementById('has_necrosis')?.checked || false,
        has_scabs: document.getElementById('has_scabs')?.checked || false,
        has_infection: document.getElementById('has_infection')?.checked || false,
        has_follicle_loss: document.getElementById('has_follicle_loss')?.checked || false,
        result_rating: document.querySelector('input[name="result_rating"]:checked')?.value || null,
        needs_another_surgery: document.getElementById('needs_another_surgery')?.checked || false
    };
    
    fetch(`/api/surgery/${surgeryId}/evolution`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': typeof getCSRFToken === 'function' ? getCSRFToken() : ''
        },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            bootstrap.Modal.getInstance(document.getElementById('surgeryEvolutionModal')).hide();
            if (typeof showAlert === 'function') showAlert('✅ Evolução salva!', 'success');
            window.loadSurgeries();
        } else {
            if (typeof showAlert === 'function') showAlert('❌ Erro: ' + result.error, 'danger');
        }
    })
    .catch(err => console.error('Erro:', err));
}

document.addEventListener('DOMContentLoaded', function() {
    const surgeriesList = document.getElementById('surgeriesList');
    if (surgeriesList && typeof patientId !== 'undefined') {
        window.loadSurgeries();
    }
});

