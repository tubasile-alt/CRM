document.addEventListener('DOMContentLoaded', function() {
    console.log("prontuario.js carregado v=20260306-clean-3");
    
    const patientId = window.location.pathname.split('/').pop();
    const urlParams = new URLSearchParams(window.location.search);
    const appointmentId = urlParams.get('appointment_id');

    // Inicialização de UI baseada em categoria
    const categoryRadios = document.querySelectorAll('input[name="category"]');
    categoryRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateUIByCategory(this.value);
        });
    });

    // Função para atualizar UI por categoria
    function updateUIByCategory(category) {
        console.log("Categoria alterada para:", category);
        const tabPlanejamento = document.getElementById('tabPlanejamento');
        const tabTransplante = document.getElementById('tabTransplante');
        const cosmeticRightColumn = document.getElementById('cosmeticRightColumn');
        const prontuarioMainLayout = document.getElementById('prontuarioMainLayout');

        if (category === 'cosmiatria') {
            if (tabPlanejamento) tabPlanejamento.style.display = 'block';
            if (tabTransplante) tabTransplante.style.display = 'none';
            if (cosmeticRightColumn) {
                cosmeticRightColumn.classList.remove('d-none');
                const leftCol = document.getElementById('prontuarioLeftColumn');
                if (leftCol) {
                    leftCol.classList.remove('col-lg-12');
                    leftCol.classList.add('col-lg-8');
                }
            }
        } else if (category === 'transplante_capilar') {
            if (tabPlanejamento) tabPlanejamento.style.display = 'none';
            if (tabTransplante) tabTransplante.style.display = 'block';
            if (cosmeticRightColumn) cosmeticRightColumn.classList.add('d-none');
            const leftCol = document.getElementById('prontuarioLeftColumn');
            if (leftCol) {
                leftCol.classList.remove('col-lg-8');
                leftCol.classList.add('col-lg-12');
            }
        } else {
            if (tabPlanejamento) tabPlanejamento.style.display = 'none';
            if (tabTransplante) tabTransplante.style.display = 'none';
            if (cosmeticRightColumn) cosmeticRightColumn.classList.add('d-none');
            const leftCol = document.getElementById('prontuarioLeftColumn');
            if (leftCol) {
                leftCol.classList.remove('col-lg-8');
                leftCol.classList.add('col-lg-12');
            }
        }
    }

    // Carregar dados iniciais
    loadConsultationHistory();
    
    // Timer de consulta
    let timerInterval;
    let seconds = 0;
    
    window.startConsultation = function() {
        console.log("Iniciando consulta...");
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            seconds++;
            const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
            const secs = (seconds % 60).toString().padStart(2, '0');
            const display = document.getElementById('timerDisplay');
            if (display) display.innerText = `${mins}:${secs}`;
        }, 1000);
        
        const startBtn = document.getElementById('startTimer');
        if (startBtn) startBtn.disabled = true;
    };

    window.finishConsultation = function() {
        console.log("Finalizando consulta...");
        clearInterval(timerInterval);
        saveConsultation();
    };

    function saveConsultation() {
        const data = {
            patient_id: patientId,
            appointment_id: appointmentId,
            category: document.querySelector('input[name="category"]:checked')?.value,
            queixa: document.getElementById('queixaText')?.value,
            anamnese: document.getElementById('anamneseText')?.value,
            diagnostico: document.getElementById('diagnosticoText')?.value,
            conduta: document.getElementById('condutaText')?.value,
            duration: seconds
        };

        fetch('/api/consultations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            alert("Atendimento finalizado e salvo com sucesso!");
            window.location.reload();
        })
        .catch(err => console.error("Erro ao salvar consulta:", err));
    }

    function loadConsultationHistory() {
        fetch(`/api/patient/${patientId}/consultations`)
        .then(res => res.json())
        .then(history => {
            const container = document.getElementById('consultationHistory');
            if (!container) return;
            
            if (!Array.isArray(history) || history.length === 0) {
                container.innerHTML = '<p class="text-muted p-3">Nenhum histórico encontrado para este paciente.</p>';
                return;
            }

            container.innerHTML = history.map(c => `
                <div class="card mb-3 border-0 bg-light shadow-sm">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold text-primary mb-0">${c.date} - ${c.category || 'Consulta'}</h6>
                            <button class="btn btn-sm btn-outline-warning" onclick="editOldConsultation(${c.id})">
                                <i class="bi bi-pencil"></i> Editar
                            </button>
                        </div>
                        <div class="small">
                            <p class="mb-1"><strong>Queixa:</strong> ${c.queixa || '-'}</p>
                            <p class="mb-0"><strong>Conduta:</strong> ${c.conduta || '-'}</p>
                        </div>
                    </div>
                </div>
            `).join('');
        });
    }

    window.startDictation = function(targetId, event) {
        if (event) event.preventDefault();
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Ditado não suportado neste navegador.");
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = 'pt-BR';
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            const textarea = document.getElementById(targetId);
            if (textarea) textarea.value += (textarea.value ? ' ' : '') + text;
        };
        recognition.start();
    };

    window.abrirDermaScribe = function() {
        alert("Integrando com DermaScribe para prescrição...");
    };

    window.addCosmeticProcedure = function() {
        const name = document.getElementById('newProcedureName').value;
        const value = document.getElementById('newProcedureValue').value;
        const months = document.getElementById('newProcedureMonths').value;
        const obs = document.getElementById('newProcedureObservations').value;

        if (!name) return alert("Selecione um procedimento.");

        const tbody = document.getElementById('cosmeticPlanBody');
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${name}</td>
            <td>R$ ${parseFloat(value || 0).toFixed(2)}</td>
            <td>${months}</td>
            <td>${obs}</td>
            <td><button class="btn btn-sm btn-outline-danger" onclick="this.closest('tr').remove(); calculateTotal();"><i class="bi bi-trash"></i></button></td>
        `;
        tbody.appendChild(tr);
        calculateTotal();
        
        // Reset inputs
        document.getElementById('newProcedureName').value = "";
        document.getElementById('newProcedureValue').value = "";
        document.getElementById('newProcedureObservations').value = "";
    };

    function calculateTotal() {
        let total = 0;
        document.querySelectorAll('#cosmeticPlanBody tr').forEach(tr => {
            const valStr = tr.cells[1].innerText.replace('R$ ', '');
            total += parseFloat(valStr) || 0;
        });
        const totalDisplay = document.getElementById('cosmeticTotal');
        if (totalDisplay) totalDisplay.innerText = `R$ ${total.toFixed(2)}`;
    }
});
