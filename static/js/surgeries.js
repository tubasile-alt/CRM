// ========== GERENCIAR CIRURGIAS ==========

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

// Salvar nova cirurgia
function saveSurgery() {
    console.log('saveSurgery chamada, patientId:', patientId);
    
    const surgeryDate = document.getElementById('surgeryDate').value;
    const surgicalData = document.getElementById('surgicalData').value.trim();
    const observations = document.getElementById('surgeryObservations').value.trim();
    
    if (!surgeryDate) {
        showAlert('⚠️ Selecione a data da cirurgia!', 'warning');
        return;
    }
    
    if (!surgicalData) {
        showAlert('⚠️ Preencha os dados cirúrgicos!', 'warning');
        return;
    }
    
    console.log('Enviando cirurgia:', { surgeryDate, surgicalData, observations });
    
    fetch(`/api/patient/${patientId}/surgery`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            surgery_date: surgeryDate,
            surgical_data: surgicalData,
            observations: observations
        })
    })
    .then(r => {
        console.log('Status:', r.status);
        return r.json();
    })
    .then(result => {
        console.log('Resultado:', result);
        if (result.success) {
            showAlert('✅ Cirurgia registrada com sucesso!', 'success');
            document.getElementById('surgeryDate').value = '';
            document.getElementById('surgicalData').value = '';
            document.getElementById('surgeryObservations').value = '';
            loadSurgeries();
        } else {
            showAlert('❌ ' + (result.error || 'Erro ao salvar cirurgia'), 'danger');
        }
    })
    .catch(err => {
        console.error('Erro ao salvar cirurgia:', err);
        showAlert('❌ Erro ao salvar cirurgia: ' + err.message, 'danger');
    });
}

// Carregar e exibir cirurgias
function loadSurgeries() {
    console.log('loadSurgeries chamada, patientId:', patientId);
    
    fetch(`/api/patient/${patientId}/surgeries`)
        .then(r => {
            console.log('Status cirurgias:', r.status);
            return r.json();
        })
        .then(surgeries => {
            console.log('Cirurgias carregadas:', surgeries);
            renderSurgeries(surgeries);
        })
        .catch(err => console.error('Erro ao carregar cirurgias:', err));
}

// Renderizar lista de cirurgias com opção de evolução
function renderSurgeries(surgeries) {
    const container = document.getElementById('surgeriesList');
    
    if (!surgeries || surgeries.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><em>Nenhuma cirurgia registrada</em></div>';
        return;
    }
    
    // Ordenar por data (mais recentes primeiro)
    const sorted = [...surgeries].sort((a, b) => new Date(b.surgery_date) - new Date(a.surgery_date));
    
    container.innerHTML = sorted.map((surgery, idx) => `
        <div class="card mb-3 border-left border-success" style="border-left: 5px solid #198754;">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h6 class="mb-2 text-success">
                            <i class="bi bi-calendar2-check"></i> 
                            <strong>${calculateSurgeryTime(surgery.surgery_date)}</strong>
                        </h6>
                        
                        <div class="mb-2">
                            <strong>📋 Dados Cirúrgicos:</strong>
                            <p class="mb-0 p-2 bg-light rounded" style="white-space: pre-wrap; font-size: 0.9rem;">
                                ${surgery.surgical_data}
                            </p>
                        </div>
                        
                        ${surgery.observations ? `
                        <div class="mb-2">
                            <strong>📝 Observações:</strong>
                            <p class="mb-0 p-2 bg-light rounded" style="white-space: pre-wrap; font-size: 0.9rem;">
                                ${surgery.observations}
                            </p>
                        </div>
                        ` : ''}
                        
                        <small class="text-muted"><i class="bi bi-person-fill"></i> Dr. ${surgery.doctor_name}</small>
                    </div>
                    <div class="col-md-4">
                        <button class="btn btn-sm btn-success w-100 mb-2" onclick="createEvolutionForSurgery(${surgery.id}, '${surgery.surgery_date}')">
                            <i class="bi bi-plus-circle"></i> Criar Evolução
                        </button>
                        <button class="btn btn-sm btn-outline-danger w-100" onclick="deleteSurgery(${surgery.id})">
                            <i class="bi bi-trash"></i> Deletar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Deletar cirurgia
function deleteSurgery(surgeryId) {
    if (!confirm('❌ Tem certeza que deseja deletar esta cirurgia? Esta ação é irreversível.')) return;
    
    fetch(`/api/patient/delete/${surgeryId}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('✅ Cirurgia deletada!', 'success');
            loadSurgeries();
        } else {
            showAlert('❌ ' + (result.error || 'Erro ao deletar'), 'danger');
        }
    })
    .catch(err => {
        console.error('Erro ao deletar cirurgia:', err);
        showAlert('❌ Erro ao deletar cirurgia', 'danger');
    });
}

// Criar evolução vinculada à cirurgia
function createEvolutionForSurgery(surgeryId, surgeryDate) {
    console.log('Criar evolução para cirurgia:', surgeryId, surgeryDate);
    
    // Navegar para aba de evoluções
    const evolutionTab = document.querySelector('[href="#evolucoes"]');
    if (evolutionTab) {
        new bootstrap.Tab(evolutionTab).show();
    }
    
    // Pré-preencher observação com referência à cirurgia
    const dateFormatted = new Date(surgeryDate).toLocaleDateString('pt-BR');
    const evolutionObservations = document.getElementById('newEvolutionObservations');
    if (evolutionObservations) {
        evolutionObservations.value = `[EVOLUÇÃO PÓS-CIRURGIA - ${dateFormatted}]\n\n`;
        evolutionObservations.focus();
    }
    
    showAlert('✏️ Aba de Evoluções aberta - Preencha os dados da evolução pós-cirurgia', 'info');
}

// Chamar ao carregar página se o elemento existir
document.addEventListener('DOMContentLoaded', function() {
    const surgeriesList = document.getElementById('surgeriesList');
    if (surgeriesList && typeof patientId !== 'undefined') {
        console.log('Carregando cirurgias na inicialização');
        loadSurgeries();
    }
});
