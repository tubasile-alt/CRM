let currentSurgeryId = null;

function openSurgeryModal() {
    currentSurgeryId = null;
    document.getElementById('surgeryDate').value = '';
    document.getElementById('surgerySurgicalPlanning').value = '';
    document.getElementById('surgeryComplications').value = '';
    new bootstrap.Modal(document.getElementById('surgeryModal')).show();
}

function saveSurgery() {
    const date = document.getElementById('surgeryDate').value;
    const planning = document.getElementById('surgerySurgicalPlanning').value;
    const complications = document.getElementById('surgeryComplications').value;
    
    if (!date) {
        showAlert('Por favor, selecione a data da cirurgia', 'warning');
        return;
    }
    
    const payload = {
        surgery_date: new Date(date).toISOString(),
        surgical_planning: planning,
        complications: complications
    };
    
    fetch(`/api/hair-transplant/${hairTransplantId}/surgeries`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Cirurgia registrada com sucesso!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('surgeryModal')).hide();
            loadSurgeries();
        } else {
            showAlert(result.error || 'Erro ao salvar', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao salvar cirurgia', 'danger');
    });
}

function loadSurgeries() {
    fetch(`/api/hair-transplant/${hairTransplantId}/surgeries`)
        .then(r => r.json())
        .then(surgeries => {
            renderSurgeries(surgeries);
        })
        .catch(err => console.error('Erro ao carregar cirurgias:', err));
}

function renderSurgeries(surgeries) {
    const list = document.getElementById('surgeriesList');
    const noMsg = document.getElementById('noSurgeriesMsg');
    
    if (surgeries.length === 0) {
        list.innerHTML = '';
        noMsg.style.display = 'block';
        return;
    }
    
    noMsg.style.display = 'none';
    list.innerHTML = surgeries.map((s, idx) => `
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#surgery${s.id}">
                    <strong>🗓️ ${new Date(s.surgery_date).toLocaleDateString('pt-BR', {hour: '2-digit', minute: '2-digit'})}</strong>
                </button>
            </h2>
            <div id="surgery${s.id}" class="accordion-collapse collapse">
                <div class="accordion-body">
                    <div class="mb-3">
                        <h6>Planejamento Cirúrgico:</h6>
                        <p>${s.surgical_planning || '<em class="text-muted">Não informado</em>'}</p>
                    </div>
                    <div class="mb-3">
                        <h6>Intercorrências:</h6>
                        <p>${s.complications || '<em class="text-muted">Sem intercorrências</em>'}</p>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteSurgery(${s.id})">
                        <i class="bi bi-trash"></i> Deletar
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function deleteSurgery(surgeryId) {
    if (!confirm('Tem certeza que deseja deletar esta cirurgia?')) return;
    
    fetch(`/api/surgery/${surgeryId}`, {
        method: 'DELETE'
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Cirurgia deletada!', 'success');
            loadSurgeries();
        } else {
            showAlert(result.error || 'Erro ao deletar', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao deletar cirurgia', 'danger');
    });
}

// Carregar cirurgias ao abrir
document.addEventListener('DOMContentLoaded', function() {
    if (typeof hairTransplantId !== 'undefined' && hairTransplantId) {
        loadSurgeries();
    }
});
