document.addEventListener('DOMContentLoaded', function() {
    const medicationInput = document.getElementById('medicationInput');
    const clearMedicationInput = document.getElementById('clearMedicationInput');
    const suggestionsList = document.getElementById('suggestionsList');
    const oralMedicationsList = document.getElementById('oralMedicationsList');
    const topicalMedicationsList = document.getElementById('topicalMedicationsList');
    const medicationCount = document.getElementById('medicationCount');
    const patientNameInput = document.getElementById('patientName');
    const templatePatientNameInput = document.getElementById('templatePatientName');
    const previewPatientName = document.getElementById('previewPatientName');
    const previewOralMedications = document.getElementById('previewOralMedications');
    const previewTopicalMedications = document.getElementById('previewTopicalMedications');
    const previewDate = document.getElementById('previewDate');
    const copyPrescription = document.getElementById('copyPrescription');
    const printPrescription = document.getElementById('printPrescription');
    const copyToast = document.getElementById('copyToast');
    const addManualMedicationBtn = document.getElementById('addManualMedication');
    const clearFormBtn = document.getElementById('clearForm');
    const exportExcelBtn = document.getElementById('exportMedicationsExcel');
    const savePrescriptionBtn = document.getElementById('savePrescription');
    const patientIdInput = document.getElementById('patientId');

    const toast = new bootstrap.Toast(copyToast);

    previewDate.textContent = new Date().toLocaleDateString('pt-BR');

    let medications = { oral: [], topical: [] };

    function updateMedicationCount() {
        const totalCount = medications.oral.length + medications.topical.length;
        medicationCount.textContent = `${totalCount}/5`;

        if (totalCount >= 5) {
            medicationInput.disabled = true;
            medicationInput.placeholder = "Limite de 5 medicamentos atingido";
        } else {
            medicationInput.disabled = false;
            medicationInput.placeholder = "Digite para buscar medicamentos...";
        }
    }

    clearMedicationInput.addEventListener('click', function() {
        medicationInput.value = '';
        suggestionsList.innerHTML = '';
        suggestionsList.classList.add('d-none');
    });

    let debounceTimer;
    medicationInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const inputValue = this.value.trim();

        if (inputValue.length < 3) {
            suggestionsList.innerHTML = '';
            suggestionsList.classList.add('d-none');
            return;
        }

        debounceTimer = setTimeout(() => {
            fetchMedicationSuggestions(inputValue);
        }, 500);
    });

    function fetchMedicationSuggestions(partialInput) {
        fetch('/dermascribe/api/suggest-medications', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ partial_input: partialInput })
        })
        .then(response => response.json())
        .then(data => {
            displaySuggestions(data.suggestions || []);
        })
        .catch(error => {
            console.error('Error fetching suggestions:', error);
            suggestionsList.innerHTML = `<div class="list-group-item text-danger">Erro ao buscar sugestões</div>`;
            suggestionsList.classList.remove('d-none');
        });
    }

    function displaySuggestions(suggestions) {
        suggestionsList.innerHTML = '';

        if (suggestions.length === 0) {
            suggestionsList.innerHTML = `<div class="list-group-item text-muted">Nenhuma sugestão encontrada</div>`;
            suggestionsList.classList.remove('d-none');
            return;
        }

        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'list-group-item suggestion-item';

            const typeClass = suggestion.type === 'topical' ? 'bg-success' : 'bg-primary';
            const typeIcon = suggestion.type === 'topical' ? 'fa-prescription-bottle' : 'fa-pills';

            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div><strong>${suggestion.medication}</strong></div>
                        <small class="text-muted">${suggestion.instructions || ''}</small>
                    </div>
                    <span class="badge ${typeClass}">
                        <i class="fas ${typeIcon} me-1"></i>
                        ${suggestion.type === 'topical' ? 'Tópico' : 'Oral'}
                    </span>
                </div>
            `;

            item.addEventListener('click', () => {
                addMedication(suggestion);
                medicationInput.value = '';
                suggestionsList.innerHTML = '';
                suggestionsList.classList.add('d-none');
            });

            suggestionsList.appendChild(item);
        });

        suggestionsList.classList.remove('d-none');
    }

    function addMedication(medication) {
        const totalCount = medications.oral.length + medications.topical.length;
        if (totalCount >= 5) {
            alert('Você atingiu o limite de 5 medicamentos por prescrição.');
            return;
        }

        const type = medication.type.toLowerCase();
        const exists = [...medications.oral, ...medications.topical].some(m =>
            m.medication.toLowerCase() === medication.medication.toLowerCase());

        if (exists) {
            alert('Este medicamento já foi adicionado à prescrição.');
            return;
        }

        if (type === 'oral') {
            medications.oral.push(medication);
        } else {
            medications.topical.push(medication);
        }

        updateMedicationsList();
        updatePreview();
        updateMedicationCount();
    }

    addManualMedicationBtn.addEventListener('click', function() {
        const medName = document.getElementById('manualMedicationName').value.trim();
        const medType = document.getElementById('manualMedicationType').value;
        const medInstructions = document.getElementById('manualMedicationInstructions').value.trim();

        if (!medName) {
            alert('Por favor, digite o nome do medicamento.');
            return;
        }

        if (!medType) {
            alert('Por favor, selecione o tipo de medicamento.');
            return;
        }

        const newMedication = {
            medication: medName,
            type: medType,
            instructions: medInstructions || (medType === 'oral' ? 'Tomar conforme orientação médica' : 'Aplicar conforme orientação médica')
        };

        addMedication(newMedication);
        saveMedicationToDatabase(newMedication);

        document.getElementById('manualMedicationName').value = '';
        document.getElementById('manualMedicationType').value = '';
        document.getElementById('manualMedicationInstructions').value = '';
    });

    function updateMedicationsList() {
        if (medications.oral.length === 0) {
            oralMedicationsList.innerHTML = '<li class="list-group-item text-muted empty-list">Nenhum medicamento oral</li>';
        } else {
            oralMedicationsList.innerHTML = '';
            medications.oral.forEach((med, index) => {
                const item = document.createElement('li');
                item.className = 'list-group-item medication-item';
                item.innerHTML = `
                    <div>
                        <div><strong>${med.medication}</strong></div>
                        <small class="text-muted">${med.instructions || ''}</small>
                    </div>
                    <div class="medication-actions">
                        <i class="fas fa-edit edit-medication" data-type="oral" data-index="${index}"></i>
                        <i class="fas fa-times remove-medication" data-type="oral" data-index="${index}"></i>
                    </div>
                `;
                oralMedicationsList.appendChild(item);
            });
        }

        if (medications.topical.length === 0) {
            topicalMedicationsList.innerHTML = '<li class="list-group-item text-muted empty-list">Nenhum medicamento tópico</li>';
        } else {
            topicalMedicationsList.innerHTML = '';
            medications.topical.forEach((med, index) => {
                const item = document.createElement('li');
                item.className = 'list-group-item medication-item';
                item.innerHTML = `
                    <div>
                        <div><strong>${med.medication}</strong></div>
                        <small class="text-muted">${med.instructions || ''}</small>
                    </div>
                    <div class="medication-actions">
                        <i class="fas fa-edit edit-medication" data-type="topical" data-index="${index}"></i>
                        <i class="fas fa-times remove-medication" data-type="topical" data-index="${index}"></i>
                    </div>
                `;
                topicalMedicationsList.appendChild(item);
            });
        }

        document.querySelectorAll('.remove-medication').forEach(btn => {
            btn.addEventListener('click', function() {
                const type = this.dataset.type;
                const index = parseInt(this.dataset.index);
                medications[type].splice(index, 1);
                updateMedicationsList();
                updatePreview();
                updateMedicationCount();
            });
        });

        document.querySelectorAll('.edit-medication').forEach(btn => {
            btn.addEventListener('click', function() {
                const type = this.dataset.type;
                const index = parseInt(this.dataset.index);
                const med = medications[type][index];
                const newInstructions = prompt('Editar posologia:', med.instructions || '');
                if (newInstructions !== null) {
                    med.instructions = newInstructions.trim() || med.instructions;
                    updateMedicationsList();
                    updatePreview();
                }
            });
        });
    }

    function updatePreview() {
        const patientName = patientNameInput.value.trim() || '______________________';
        previewPatientName.textContent = patientName;

        if (medications.oral.length === 0) {
            previewOralMedications.classList.add('d-none');
        } else {
            previewOralMedications.classList.remove('d-none');
            const list = previewOralMedications.querySelector('.medication-list');
            list.innerHTML = '';
            medications.oral.forEach(med => {
                const item = document.createElement('li');
                item.innerHTML = `<strong>${med.medication}</strong>${med.instructions ? `<br><span>${med.instructions}</span>` : ''}`;
                list.appendChild(item);
            });
        }

        if (medications.topical.length === 0) {
            previewTopicalMedications.classList.add('d-none');
        } else {
            previewTopicalMedications.classList.remove('d-none');
            const list = previewTopicalMedications.querySelector('.medication-list');
            list.innerHTML = '';
            medications.topical.forEach(med => {
                const item = document.createElement('li');
                item.innerHTML = `<strong>${med.medication}</strong>${med.instructions ? `<br><span>${med.instructions}</span>` : ''}`;
                list.appendChild(item);
            });
        }
    }

    patientNameInput.addEventListener('input', updatePreview);

    function saveMedicationToDatabase(medication) {
        fetch('/dermascribe/api/save-medication', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(medication)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const saveToast = new bootstrap.Toast(document.getElementById('saveToast'));
                saveToast.show();
            }
        })
        .catch(error => console.error('Erro ao salvar medicamento:', error));
    }

    copyPrescription.addEventListener('click', function() {
        const preview = document.getElementById('prescriptionPreview');
        const text = preview.innerText;
        navigator.clipboard.writeText(text).then(() => {
            toast.show();
        });
    });

    printPrescription.addEventListener('click', function() {
        window.print();
    });

    clearFormBtn.addEventListener('click', function() {
        medications = { oral: [], topical: [] };
        patientNameInput.value = '';
        updateMedicationsList();
        updatePreview();
        updateMedicationCount();
    });

    exportExcelBtn.addEventListener('click', function() {
        window.location.href = '/dermascribe/api/export-medications-excel';
    });

    const useTransplantTemplate = document.getElementById('useTransplantTemplate');
    if (useTransplantTemplate) {
        useTransplantTemplate.addEventListener('click', function() {
            const patientName = templatePatientNameInput.value.trim();
            if (!patientName) {
                alert('Por favor, informe o nome do paciente.');
                return;
            }

            medications = { oral: [], topical: [] };

            medications.topical.push({
                medication: 'CAPPY',
                type: 'topical',
                instructions: 'APLICAR NO COURO CABELUDO 1X/DIA'
            });

            medications.oral.push({
                medication: 'NEOSIL ATTACK',
                type: 'oral',
                instructions: 'TOMAR 01 CP VO POR DIA POR 3 MESES'
            });

            medications.oral.push({
                medication: 'MINOXIDIL 2,5MG',
                type: 'oral',
                instructions: 'TOMAR 01 CP VO POR DIA'
            });

            patientNameInput.value = patientName;
            updateMedicationsList();
            updatePreview();
            updateMedicationCount();

            document.getElementById('custom-tab').click();
        });
    }

    const analyticsTab = document.getElementById('analytics-tab');
    if (analyticsTab) {
        analyticsTab.addEventListener('shown.bs.tab', function() {
            loadTopMedications();
        });
    }

    function loadTopMedications() {
        const container = document.getElementById('topMedicationsContainer');

        fetch('/dermascribe/api/analytics/top-medications')
        .then(response => response.json())
        .then(data => {
            if (data.medications.length === 0) {
                container.innerHTML = '<p class="text-center text-muted">Nenhum dado de prescrição disponível ainda.</p>';
                return;
            }

            let html = '<table class="table table-striped"><thead><tr><th>#</th><th>Medicamento</th><th>Tipo</th><th>Prescrições</th></tr></thead><tbody>';
            data.medications.forEach((med, index) => {
                const typeLabel = med.type === 'topical' ? 'Tópico' : 'Oral';
                const typeBadge = med.type === 'topical' ? 'bg-success' : 'bg-primary';
                html += `<tr>
                    <td>${index + 1}</td>
                    <td>${med.name}</td>
                    <td><span class="badge ${typeBadge}">${typeLabel}</span></td>
                    <td>${med.count}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        })
        .catch(error => {
            container.innerHTML = '<p class="text-danger text-center">Erro ao carregar estatísticas.</p>';
        });
    }

    if (patientNameInput.value) {
        updatePreview();
    }

    // ==============================
    // PATCH FINAL (ROBUSTO) - SALVAR + IMPRIMIR
    // ==============================
    async function handleSaveAndPrint(e) {
        if (e) e.preventDefault();
        
        // Evita duplo clique
        if (savePrescriptionBtn && savePrescriptionBtn.dataset.loading === '1') return;

        const patient_id = patientIdInput?.value?.trim();
        const patient_name = patientNameInput?.value?.trim() || '';

        if (!patient_id) {
            alert('ID do paciente é obrigatório. Abra esta página a partir do prontuário.');
            return;
        }

        // Coleta medicamentos das variáveis locais (medications.oral / medications.topical)
        if (medications.oral.length === 0 && medications.topical.length === 0) {
            const ok = confirm('Nenhum medicamento foi adicionado. Deseja salvar mesmo assim?');
            if (!ok) return;
        }

        const setButtonLoading = (isLoading) => {
            if (savePrescriptionBtn) {
                savePrescriptionBtn.disabled = isLoading;
                savePrescriptionBtn.style.opacity = isLoading ? '0.6' : '1';
                savePrescriptionBtn.style.cursor = isLoading ? 'not-allowed' : 'pointer';
                savePrescriptionBtn.dataset.loading = isLoading ? '1' : '0';
                if (isLoading) {
                    savePrescriptionBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Salvando...';
                } else {
                    savePrescriptionBtn.innerHTML = '<i class="fas fa-save me-2"></i>Salvar Receita no Prontuário';
                }
            }
        };

        setButtonLoading(true);

        try {
            const res = await fetch('/dermascribe/api/save-prescription', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    patient_id: Number(patient_id),
                    patient_name: patient_name,
                    oral: medications.oral,
                    topical: medications.topical
                })
            });

            const data = await res.json();

            if (data.status === 'success') {
                const prescriptionId = data.prescription_id;
                
                if (prescriptionId) {
                    // Abrir impressão em nova aba (rota profissional)
                    const pdfUrl = `/dermascribe/prescription/${prescriptionId}/pdf`;
                    window.open(pdfUrl, '_blank', 'noopener,noreferrer');
                }

                if (window.opener && !window.opener.closed) {
                    window.opener.postMessage({
                        type: 'prescription_saved',
                        prescription_id: prescriptionId,
                        patient_id: patient_id
                    }, '*');
                }
                
                alert('Receita salva com sucesso!');
                setTimeout(() => window.close(), 500);
            } else {
                alert('Erro ao salvar receita: ' + (data.message || 'Erro desconhecido'));
            }
        } catch (error) {
            console.error('Erro ao salvar receita:', error);
            alert('Falha ao salvar: ' + error.message);
        } finally {
            setButtonLoading(false);
        }
    }

    if (savePrescriptionBtn) {
        savePrescriptionBtn.addEventListener('click', handleSaveAndPrint);
    }

    if (printPrescription) {
        printPrescription.addEventListener('click', handleSaveAndPrint);
    }
});
