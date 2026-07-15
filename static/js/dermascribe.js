    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }
    function fetchHeaders(contentType) {
        const h = {};
        if (contentType) h['Content-Type'] = contentType;
        const csrf = getCsrfToken();
        if (csrf) h['X-CSRFToken'] = csrf;
        return h;
    }

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
            headers: fetchHeaders('application/json'),
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

            const catBadge = suggestion.categoria ? `<span class="badge bg-light text-dark border ms-1" style="font-size:0.65em;">${suggestion.categoria}</span>` : '';
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div><strong>${suggestion.medication}</strong>${catBadge}</div>
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
                saveMedicationToDatabase(suggestion);
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

    function updatePreview(oralMeds, topicalMeds, patientNameOverride) {
        const patientName = patientNameOverride !== undefined
            ? patientNameOverride
            : (patientNameInput.value.trim() || '______________________');
        previewPatientName.textContent = patientName;

        const oMeds = oralMeds !== undefined ? oralMeds : medications.oral;
        const tMeds = topicalMeds !== undefined ? topicalMeds : medications.topical;

        if (oMeds.length === 0) {
            previewOralMedications.classList.add('d-none');
        } else {
            previewOralMedications.classList.remove('d-none');
            const list = previewOralMedications.querySelector('.medication-list');
            list.innerHTML = '';
            oMeds.forEach(med => {
                const item = document.createElement('li');
                item.innerHTML = `<strong>${med.medication}</strong>${med.instructions ? `<br><span>${med.instructions}</span>` : ''}`;
                list.appendChild(item);
            });
        }

        if (tMeds.length === 0) {
            previewTopicalMedications.classList.add('d-none');
        } else {
            previewTopicalMedications.classList.remove('d-none');
            const list = previewTopicalMedications.querySelector('.medication-list');
            list.innerHTML = '';
            tMeds.forEach(med => {
                const item = document.createElement('li');
                item.innerHTML = `<strong>${med.medication}</strong>${med.instructions ? `<br><span>${med.instructions}</span>` : ''}`;
                list.appendChild(item);
            });
        }
    }

    patientNameInput.addEventListener('input', function() { updatePreview(); });

    window._dermascribeUpdatePreview = updatePreview;
    window._addMedication = addMedication;
    window._saveMedicationToDatabase = saveMedicationToDatabase;

    function saveMedicationToDatabase(medication, onCategorized) {
        fetch('/dermascribe/api/save-medication', {
            method: 'POST',
            headers: fetchHeaders('application/json'),
            body: JSON.stringify(medication)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const saveToast = new bootstrap.Toast(document.getElementById('saveToast'));
                saveToast.show();
                // Abrir modal de categorização para medicamento NOVO
                if (window._openCategorizarModal) {
                    window._openCategorizarModal(medication.medication, medication.type, medication.instructions, function(didCategorize) {
                        if (onCategorized) onCategorized(didCategorize);
                    });
                } else if (onCategorized) {
                    onCategorized(false);
                }
            } else if (data.status === 'exists') {
                // Medicamento já existe - modal NÃO abre
                if (onCategorized) onCategorized(false);
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

            // USO TÓPICO
            medications.topical.push({
                medication: 'PIELLUS MX',
                type: 'topical',
                instructions: 'APLICAR NO COURO CABELUDO 1X/DIA'
            });

            // USO INTERNO
            medications.oral.push({
                medication: 'NOUVE SILÍCIO D',
                type: 'oral',
                instructions: 'TOMAR 01 CP VO POR DIA POR 3 MESES'
            });
            medications.oral.push({
                medication: 'MINOXIDIL 2,5MG',
                type: 'oral',
                instructions: 'TOMAR 01 CP VO POR DIA (USO CONTÍNUO)'
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

        fetch('/dermascribe/api/analytics/top-medications', { credentials: 'same-origin' })
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

        // Abre janela IMEDIATAMENTE (no gesto do clique) para evitar bloqueio do popup
        let printWin;
        try {
            printWin = window.open('about:blank', '_blank');
        } catch (err) {
            console.error('Falha ao abrir janela de impressão:', err);
        }
        if (!printWin) {
            alert('O navegador bloqueou a janela de impressão. Permita popups para este site.');
            return;
        }

        // Evita duplo clique
        if (savePrescriptionBtn && savePrescriptionBtn.dataset.loading === '1') {
            printWin.close();
            return;
        }

        const patient_id = patientIdInput?.value?.trim();
        const patient_name = patientNameInput?.value?.trim() || '';

        if (!patient_id) {
            alert('ID do paciente é obrigatório. Abra esta página a partir do prontuário.');
            printWin.close();
            return;
        }

        // Coleta medicamentos das variáveis locais (medications.oral / medications.topical)
        if (medications.oral.length === 0 && medications.topical.length === 0) {
            const ok = confirm('Nenhum medicamento foi adicionado. Deseja salvar mesmo assim?');
            if (!ok) {
                printWin.close();
                return;
            }
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
                headers: fetchHeaders('application/json'),
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

                if (prescriptionId && printWin && !printWin.closed) {
                    try {
                        printWin.location.href = `/dermascribe/prescription/${prescriptionId}/print`;
                    } catch (err) {
                        console.error('Erro ao navegar janela de impressão:', err);
                        printWin.close();
                    }
                } else if (printWin && !printWin.closed) {
                    printWin.close();
                }

                if (window.opener && !window.opener.closed) {
                    window.opener.postMessage({
                        type: 'prescription_saved',
                        prescription_id: prescriptionId,
                        patient_id: patient_id
                    }, '*');
                }

                // Notifica sucesso sem fechar a janela do DermaScribe
                const saveToast = new bootstrap.Toast(document.getElementById('saveToast'));
                if (saveToast) saveToast.show();

                // Bloco 3: Modal de categorização para medicamentos NOVOS criados via receita
                if (data.new_medications && data.new_medications.length > 0 && window._openCategorizarModal) {
                    data.new_medications.forEach(function(nm) {
                        window._openCategorizarModal(nm.name, nm.type, nm.instructions || '', function(){});
                    });
                }
            } else {
                alert('Erro ao salvar receita: ' + (data.message || 'Erro desconhecido'));
                printWin.close();
            }
        } catch (error) {
            console.error('Erro ao salvar receita:', error);
            alert('Falha ao salvar: ' + error.message);
            printWin.close();
        } finally {
            setButtonLoading(false);
        }
    }

    if (savePrescriptionBtn) {
        savePrescriptionBtn.addEventListener('click', handleSaveAndPrint);
    }

    // Botão Imprimir = imprime sem salvar (funciona sem patient_id)
    if (printPrescription) {
        printPrescription.addEventListener('click', async function(e) {
            if (e) e.preventDefault();

            if (medications.oral.length === 0 && medications.topical.length === 0) {
                alert('Adicione pelo menos um medicamento antes de imprimir.');
                return;
            }

            const patient_name = patientNameInput?.value?.trim() || '';

            let printWin;
            try {
                printWin = window.open('about:blank', '_blank');
            } catch (err) {
                console.error('Falha ao abrir janela:', err);
            }
            if (!printWin) {
                alert('O navegador bloqueou a janela de impressão. Permita popups para este site.');
                return;
            }

            try {
                const res = await fetch('/dermascribe/preview-print', {
                    method: 'POST',
                    headers: fetchHeaders('application/json'),
                    body: JSON.stringify({
                        patient_name: patient_name,
                        oral: medications.oral,
                        topical: medications.topical,
                        prescription_type: 'standard'
                    })
                });
                const html = await res.text();
                printWin.document.open();
                printWin.document.write(html);
                printWin.document.close();
            } catch (err) {
                console.error('Erro ao gerar preview de impressão:', err);
                alert('Falha ao gerar impressão.');
                printWin.close();
            }
        });
    }
});

// ==========================================================
// Controlador isolado: Antibiótico e Isotretinoína
// ==========================================================
function initSpecialtyTab(tabType) {
    const pidInput = document.getElementById(tabType + 'PatientId');
    const pnameInput = document.getElementById(tabType + 'PatientName');
    const saveBtn = document.getElementById(tabType + 'Save');
    const printBtn = document.getElementById(tabType + 'Print');
    if (!saveBtn) return;

    // Detecta modo dual (Antibiótico = Oral + Tópico)
    const isDual = tabType === 'antibiotico' && document.getElementById(tabType + 'OralMedName');

    if (isDual) {
        // ======== MODO DUAL: Oral + Tópico ========
        const oralName  = document.getElementById(tabType + 'OralMedName');
        const oralInstr = document.getElementById(tabType + 'OralMedInstr');
        const oralAdd   = document.getElementById(tabType + 'AddOral');
        const oralList  = document.getElementById(tabType + 'OralList');

        const topName  = document.getElementById(tabType + 'TopMedName');
        const topInstr = document.getElementById(tabType + 'TopMedInstr');
        const topAdd   = document.getElementById(tabType + 'AddTop');
        const topList  = document.getElementById(tabType + 'TopList');

        let oralMeds = [];
        let topMeds  = [];

        function renderOral() {
            oralList.innerHTML = '';
            if (oralMeds.length === 0) {
                oralList.innerHTML = '<li class="list-group-item text-muted">Nenhum medicamento oral adicionado</li>';
                return;
            }
            oralMeds.forEach(function(med, idx) {
                const li = document.createElement('li');
                li.className = 'list-group-item medication-item';
                li.innerHTML = '<div><strong class="text-primary">' + med.medication + '</strong><br><small>' + med.instructions + '</small></div>' +
                    '<div class="medication-actions"><i class="fas fa-trash-alt" title="Remover" data-type="oral" data-idx="' + idx + '"></i></div>';
                oralList.appendChild(li);
            });
            bindTrash(oralList, 'oral');
        }
        function renderTop() {
            topList.innerHTML = '';
            if (topMeds.length === 0) {
                topList.innerHTML = '<li class="list-group-item text-muted">Nenhum medicamento tópico adicionado</li>';
                return;
            }
            topMeds.forEach(function(med, idx) {
                const li = document.createElement('li');
                li.className = 'list-group-item medication-item';
                li.innerHTML = '<div><strong class="text-success">' + med.medication + '</strong><br><small>' + med.instructions + '</small></div>' +
                    '<div class="medication-actions"><i class="fas fa-trash-alt" title="Remover" data-type="topical" data-idx="' + idx + '"></i></div>';
                topList.appendChild(li);
            });
            bindTrash(topList, 'topical');
        }
        function bindTrash(container, t) {
            container.querySelectorAll('.fa-trash-alt').forEach(function(icon) {
                icon.addEventListener('click', function() {
                    const arr = t === 'oral' ? oralMeds : topMeds;
                    arr.splice(parseInt(this.dataset.idx), 1);
                    if (t === 'oral') renderOral(); else renderTop();
                    updatePreviewDual();
                });
            });
        }
        function updatePreviewDual() {
            if (typeof window._dermascribeUpdatePreview === 'function') {
                const pname = (pnameInput.value || '').trim();
                window._dermascribeUpdatePreview(oralMeds, topMeds, pname || undefined);
            }
        }

        renderOral();
        renderTop();

        oralAdd.addEventListener('click', function() {
            const name = (oralName.value || '').trim();
            const instr = (oralInstr.value || '').trim();
            if (!name) { alert('Digite o nome do medicamento oral.'); return; }
            if (!instr) { alert('Selecione a posologia oral.'); return; }
            oralMeds.push({ medication: name, instructions: instr, type: 'oral' });
            oralName.value = ''; oralInstr.value = ''; oralName.focus();
            renderOral(); updatePreviewDual();
        });
        topAdd.addEventListener('click', function() {
            const name = (topName.value || '').trim();
            const instr = (topInstr.value || '').trim();
            if (!name) { alert('Digite o nome do medicamento tópico.'); return; }
            if (!instr) { alert('Selecione a posologia tópica.'); return; }
            topMeds.push({ medication: name, instructions: instr, type: 'topical' });
            topName.value = ''; topInstr.value = ''; topName.focus();
            renderTop(); updatePreviewDual();
        });

        function allMeds() { return oralMeds.concat(topMeds); }

        async function saveAndPrintDual(e) {
            if (e) e.preventDefault();
            const patient_id = pidInput?.value?.trim();
            const patient_name = pnameInput?.value?.trim() || '';
            if (!patient_id) { alert('ID do paciente é obrigatório.'); return; }
            if (allMeds().length === 0) { alert('Adicione pelo menos um medicamento.'); return; }

            let printWin;
            try { printWin = window.open('about:blank', '_blank'); } catch (err) {}
            if (!printWin) { alert('Permita popups para este site.'); return; }

            try {
                const res = await fetch('/dermascribe/api/save-prescription', {
                    method: 'POST',
                    headers: fetchHeaders('application/json'),
                    body: JSON.stringify({
                        patient_id: Number(patient_id),
                        patient_name: patient_name,
                        oral: oralMeds,
                        topical: topMeds,
                        prescription_type: tabType
                    })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    const prescriptionId = data.prescription_id;
                    if (prescriptionId && printWin && !printWin.closed) {
                        try { printWin.location.href = '/dermascribe/prescription/' + prescriptionId + '/print'; }
                        catch (err) { printWin.close(); }
                    } else { printWin.close(); }
                    oralMeds = []; topMeds = [];
                    renderOral(); renderTop();
                } else {
                    alert('Erro ao salvar: ' + (data.message || 'Erro desconhecido'));
                    printWin.close();
                }
            } catch (err) {
                alert('Falha ao salvar: ' + err.message);
                printWin.close();
            }
        }
        saveBtn.addEventListener('click', saveAndPrintDual);

        if (printBtn) {
            printBtn.addEventListener('click', async function(e) {
                if (e) e.preventDefault();
                if (allMeds().length === 0) { alert('Adicione pelo menos um medicamento antes de imprimir.'); return; }
                const patient_name = pnameInput?.value?.trim() || '';
                let printWin;
                try { printWin = window.open('about:blank', '_blank'); } catch (err) {}
                if (!printWin) { alert('Permita popups para este site.'); return; }
                try {
                    const res = await fetch('/dermascribe/preview-print', {
                        method: 'POST',
                        headers: fetchHeaders('application/json'),
                        body: JSON.stringify({
                            patient_name: patient_name,
                            oral: oralMeds,
                            topical: topMeds,
                            prescription_type: tabType
                        })
                    });
                    const html = await res.text();
                    printWin.document.open();
                    printWin.document.write(html);
                    printWin.document.close();
                } catch (err) {
                    alert('Falha ao gerar impressão.');
                    printWin.close();
                }
            });
        }
        return; // fim do modo dual
    }

    // ======== MODO SINGLE (Isotretinoína etc) ========
    const medNameInput = document.getElementById(tabType + 'MedName');
    const medInstrInput = document.getElementById(tabType + 'MedInstr');
    const addBtn = document.getElementById(tabType + 'AddMed');
    const listEl = document.getElementById(tabType + 'MedList');
    if (!addBtn || !listEl) return;

    let meds = [];

    function renderList() {
        listEl.innerHTML = '';
        if (meds.length === 0) {
            listEl.innerHTML = '<li class="list-group-item text-muted">Nenhum medicamento adicionado</li>';
            return;
        }
        meds.forEach(function(med, idx) {
            const li = document.createElement('li');
            li.className = 'list-group-item medication-item';
            li.innerHTML = '<div><strong>' + med.medication + '</strong><br><small>' + med.instructions + '</small></div>' +
                '<div class="medication-actions"><i class="fas fa-trash-alt" title="Remover" data-idx="' + idx + '"></i></div>';
            listEl.appendChild(li);
        });
        listEl.querySelectorAll('.fa-trash-alt').forEach(function(icon) {
            icon.addEventListener('click', function() {
                meds.splice(parseInt(this.dataset.idx), 1);
                renderList();
                if (typeof window._dermascribeUpdatePreview === 'function') {
                    const pname = (pnameInput.value || '').trim();
                    window._dermascribeUpdatePreview(meds, [], pname || undefined);
                }
            });
        });
    }

    renderList();

    addBtn.addEventListener('click', function() {
        const name = (medNameInput.value || '').trim();
        const instr = (medInstrInput.value || '').trim();
        if (!name) { alert('Digite o nome do medicamento.'); return; }
        if (!instr) { alert('Selecione a posologia.'); return; }
        meds.push({ medication: name, instructions: instr, type: 'oral' });
        medNameInput.value = ''; medInstrInput.value = ''; medNameInput.focus();
        renderList();
        if (typeof window._dermascribeUpdatePreview === 'function') {
            const pname = (pnameInput.value || '').trim();
            window._dermascribeUpdatePreview(meds, [], pname || undefined);
        }
    });

    async function saveAndPrint(e) {
        if (e) e.preventDefault();
        const patient_id = pidInput?.value?.trim();
        const patient_name = pnameInput?.value?.trim() || '';
        if (!patient_id) { alert('ID do paciente é obrigatório.'); return; }
        if (meds.length === 0) { alert('Adicione pelo menos um medicamento.'); return; }

        let printWin;
        try { printWin = window.open('about:blank', '_blank'); } catch (err) {}
        if (!printWin) { alert('Permita popups para este site.'); return; }

        try {
            const res = await fetch('/dermascribe/api/save-prescription', {
                method: 'POST',
                headers: fetchHeaders('application/json'),
                body: JSON.stringify({
                    patient_id: Number(patient_id),
                    patient_name: patient_name,
                    oral: meds,
                    topical: [],
                    prescription_type: tabType
                })
            });
            const data = await res.json();
            if (data.status === 'success') {
                const prescriptionId = data.prescription_id;
                if (prescriptionId && printWin && !printWin.closed) {
                    try { printWin.location.href = '/dermascribe/prescription/' + prescriptionId + '/print'; }
                    catch (err) { printWin.close(); }
                } else { printWin.close(); }
                meds = []; renderList();
            } else {
                alert('Erro ao salvar: ' + (data.message || 'Erro desconhecido'));
                printWin.close();
            }
        } catch (err) {
            alert('Falha ao salvar: ' + err.message);
            printWin.close();
        }
    }
    saveBtn.addEventListener('click', saveAndPrint);

    if (printBtn) {
        printBtn.addEventListener('click', async function(e) {
            if (e) e.preventDefault();
            if (meds.length === 0) { alert('Adicione pelo menos um medicamento antes de imprimir.'); return; }
            const patient_name = pnameInput?.value?.trim() || '';
            let printWin;
            try { printWin = window.open('about:blank', '_blank'); } catch (err) {}
            if (!printWin) { alert('Permita popups para este site.'); return; }
            try {
                const res = await fetch('/dermascribe/preview-print', {
                    method: 'POST',
                    headers: fetchHeaders('application/json'),
                    body: JSON.stringify({
                        patient_name: patient_name,
                        oral: meds,
                        topical: [],
                        prescription_type: tabType
                    })
                });
                const html = await res.text();
                printWin.document.open();
                printWin.document.write(html);
                printWin.document.close();
            } catch (err) {
                alert('Falha ao gerar impressão.');
                printWin.close();
            }
        });
    }
}

// ==========================================================
// BLOCO 3 - Modal de Categorização + BLOCO 4 - Descoberta
// ==========================================================
(function() {
    let taxonomia = { categorias: [], indicacoes: [] };
    let catModalInstance = null;
    let catMedNomeAtual = '';
    let catMedTypeAtual = '';
    let catMedInstrAtual = '';
    let catIndicacoesSelecionadas = [];
    let pendingCategorizeCallback = null;

    function loadTaxonomia() {
        fetch('/dermascribe/api/taxonomia', { credentials: 'same-origin' })
            .then(function(r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function(data) {
                taxonomia = data;
                renderDescobrirCategorias();
                renderDescobrirIndicacoes();
            })
            .catch(function(e) {
                console.error('Erro taxonomia:', e);
            });
    }

    // -------- Modal de Categorização --------
    function openCategorizarModal(medName, medType, medInstr, onDone) {
        catMedNomeAtual = medName;
        catMedTypeAtual = medType;
        catMedInstrAtual = medInstr;
        pendingCategorizeCallback = onDone || function(){};
        catIndicacoesSelecionadas = [];

        document.getElementById('catMedNome').textContent = medName;
        const sel = document.getElementById('catCategoriaSelect');
        sel.innerHTML = '<option value="">Selecione...</option>';
        (taxonomia.categorias || []).forEach(function(c) {
            sel.innerHTML += '<option value="' + c + '">' + c + '</option>';
        });
        document.getElementById('catCategoriaNova').classList.add('d-none');
        document.getElementById('catCategoriaNova').value = '';
        document.getElementById('catCategoriaSelect').classList.remove('d-none');
        renderCatIndicacoesChips();
        document.getElementById('catIndicacoesSelecionadas').innerHTML = '';
        document.getElementById('catIndicacaoNova').value = '';

        if (!catModalInstance) {
            catModalInstance = new bootstrap.Modal(document.getElementById('categorizarModal'));
        }
        catModalInstance.show();
    }

    function renderCatIndicacoesChips() {
        const container = document.getElementById('catIndicacoesChips');
        container.innerHTML = '';
        (taxonomia.indicacoes || []).forEach(function(ind) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-sm btn-outline-info';
            btn.textContent = ind;
            btn.addEventListener('click', function() {
                toggleIndicacao(ind);
            });
            container.appendChild(btn);
        });
    }

    function toggleIndicacao(ind) {
        const idx = catIndicacoesSelecionadas.indexOf(ind);
        if (idx >= 0) {
            catIndicacoesSelecionadas.splice(idx, 1);
        } else {
            catIndicacoesSelecionadas.push(ind);
        }
        renderIndicacoesSelecionadas();
    }

    function renderIndicacoesSelecionadas() {
        const container = document.getElementById('catIndicacoesSelecionadas');
        container.innerHTML = '';
        catIndicacoesSelecionadas.forEach(function(ind) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-info text-dark me-1';
            badge.innerHTML = ind + ' <i class="fas fa-times" style="cursor:pointer"></i>';
            badge.querySelector('i').addEventListener('click', function() {
                toggleIndicacao(ind);
            });
            container.appendChild(badge);
        });
    }

    function salvarCategorizacao() {
        const catSel = document.getElementById('catCategoriaSelect').value;
        const catNova = document.getElementById('catCategoriaNova').value.trim();
        const categoria = catNova || catSel;
        if (!categoria) {
            alert('Selecione ou digite uma categoria.');
            return;
        }
        fetch('/dermascribe/api/save-medication', {
            method: 'POST',
            headers: fetchHeaders('application/json'),
            body: JSON.stringify({
                medication: catMedNomeAtual,
                type: catMedTypeAtual || 'topical',
                instructions: catMedInstrAtual || '',
                categoria: categoria,
                indicacoes: catIndicacoesSelecionadas.length ? catIndicacoesSelecionadas : null,
                etiqueta_revisada: true
            })
        })
        .then(r => r.json())
        .then(function(data) {
            if (data.status === 'success' || data.status === 'exists') {
                catModalInstance.hide();
                pendingCategorizeCallback(true);
                loadTaxonomia(); // atualizar chips descoberta
            }
        })
        .catch(e => console.error('Erro salvar cat:', e));
    }

    // -------- Descoberta por filtros (Bloco 4) --------
    let descobrirCatAtiva = null;
    let descobrirIndAtiva = null;
    let descobrirMostrarMais = { cat: false, ind: false };

    function renderDescobrirCategorias() {
        const container = document.getElementById('descobrirCategorias');
        if (!container) return;
        const cats = taxonomia.categorias || [];
        if (!cats.length) return;
        const mostrar = descobrirMostrarMais.cat ? cats : cats.slice(0, 10);
        container.innerHTML = '';
        mostrar.forEach(function(c) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-sm ' + (descobrirCatAtiva === c ? 'btn-primary' : 'btn-outline-primary');
            btn.style.marginRight = '4px';
            btn.style.marginBottom = '4px';
            btn.textContent = c;
            btn.addEventListener('click', function() {
                descobrirCatAtiva = descobrirCatAtiva === c ? null : c;
                renderDescobrirCategorias();
                renderDescobrirIndicacoes();
                buscarDescobrir();
            });
            container.appendChild(btn);
        });
        if (cats.length > 10) {
            const mais = document.createElement('button');
            mais.type = 'button';
            mais.className = 'btn btn-sm btn-link';
            mais.textContent = descobrirMostrarMais.cat ? 'menos...' : 'mais...';
            mais.addEventListener('click', function() {
                descobrirMostrarMais.cat = !descobrirMostrarMais.cat;
                renderDescobrirCategorias();
            });
            container.appendChild(mais);
        }
    }

    function renderDescobrirIndicacoes() {
        const container = document.getElementById('descobrirIndicacoes');
        if (!container) return;
        const inds = taxonomia.indicacoes || [];
        if (!inds.length) return;
        const mostrar = descobrirMostrarMais.ind ? inds : inds.slice(0, 10);
        container.innerHTML = '';
        mostrar.forEach(function(ind) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-sm ' + (descobrirIndAtiva === ind ? 'btn-success' : 'btn-outline-success');
            btn.style.marginRight = '4px';
            btn.style.marginBottom = '4px';
            btn.textContent = ind;
            btn.addEventListener('click', function() {
                descobrirIndAtiva = descobrirIndAtiva === ind ? null : ind;
                renderDescobrirIndicacoes();
                buscarDescobrir();
            });
            container.appendChild(btn);
        });
        if (inds.length > 10) {
            const mais = document.createElement('button');
            mais.type = 'button';
            mais.className = 'btn btn-sm btn-link';
            mais.textContent = descobrirMostrarMais.ind ? 'menos...' : 'mais...';
            mais.addEventListener('click', function() {
                descobrirMostrarMais.ind = !descobrirMostrarMais.ind;
                renderDescobrirIndicacoes();
            });
            container.appendChild(mais);
        }
    }

    function buscarDescobrir() {
        const container = document.getElementById('descobrirResultados');
        const aviso = document.getElementById('descobrirAviso');
        if (!descobrirCatAtiva && !descobrirIndAtiva) {
            container.innerHTML = '<div class="list-group-item text-muted text-center py-2">Selecione uma categoria ou indicação</div>';
            if (aviso) aviso.classList.add('d-none');
            return;
        }
        let url = '/dermascribe/api/descobrir?';
        if (descobrirCatAtiva) url += 'categoria=' + encodeURIComponent(descobrirCatAtiva) + '&';
        if (descobrirIndAtiva) url += 'indicacao=' + encodeURIComponent(descobrirIndAtiva);
        fetch(url, { credentials: 'same-origin' })
            .then(r => r.json())
            .then(function(data) {
                container.innerHTML = '';
                if (!data.medicamentos || data.medicamentos.length === 0) {
                    container.innerHTML = '<div class="list-group-item text-muted text-center py-2">Nenhum medicamento encontrado</div>';
                } else {
                    data.medicamentos.forEach(function(med) {
                        const item = document.createElement('div');
                        item.className = 'list-group-item list-group-item-action py-2';
                        const inds = (med.indicacoes || []).join(', ');
                        item.innerHTML = '<div class="d-flex justify-content-between"><strong>' + med.name + '</strong><small class="text-muted">' + (med.brand || '') + '</small></div>' +
                            '<small class="text-muted">' + inds + '</small>';
                        item.addEventListener('click', function() {
                            if (typeof window._addMedication === 'function') {
                                window._addMedication({
                                    medication: med.name,
                                    type: med.type,
                                    instructions: med.instructions || ''
                                });
                            }
                        });
                        container.appendChild(item);
                    });
                }
                if (aviso) {
                    if (data.sem_etiqueta > 0) {
                        aviso.textContent = data.sem_etiqueta + ' medicamento(s) ainda sem categoria não aparecem nos filtros';
                        aviso.classList.remove('d-none');
                    } else {
                        aviso.classList.add('d-none');
                    }
                }
            })
            .catch(e => console.error('Erro descobrir:', e));
    }

    // -------- Bindings DOM --------
    function _initBindings() {
        loadTaxonomia();

        // Toggle descobrir panel
        const toggleDesc = document.getElementById('toggleDescobrir');
        if (toggleDesc) {
            toggleDesc.addEventListener('click', function() {
                const panel = document.getElementById('descobrirPanel');
                const bsCollapse = bootstrap.Collapse.getInstance(panel);
                if (bsCollapse) {
                    bsCollapse.toggle();
                } else {
                    new bootstrap.Collapse(panel, { toggle: true });
                }
                const icon = this.querySelector('i');
                icon.classList.toggle('fa-chevron-down');
                icon.classList.toggle('fa-chevron-up');
            });
        }

        // Modal: toggle nova categoria
        const catToggleNova = document.getElementById('catToggleNova');
        if (catToggleNova) {
            catToggleNova.addEventListener('click', function() {
                const sel = document.getElementById('catCategoriaSelect');
                const inp = document.getElementById('catCategoriaNova');
                if (inp.classList.contains('d-none')) {
                    sel.classList.add('d-none');
                    inp.classList.remove('d-none');
                    inp.focus();
                    catToggleNova.innerHTML = '<i class="fas fa-list me-1"></i>Escolher existente...';
                } else {
                    sel.classList.remove('d-none');
                    inp.classList.add('d-none');
                    catToggleNova.innerHTML = '<i class="fas fa-plus me-1"></i>Nova categoria...';
                }
            });
        }

        // Modal: nova indicação por Enter
        const catIndicacaoNova = document.getElementById('catIndicacaoNova');
        if (catIndicacaoNova) {
            catIndicacaoNova.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const val = this.value.trim().toLowerCase();
                    if (val) {
                        if (catIndicacoesSelecionadas.indexOf(val) < 0) {
                            catIndicacoesSelecionadas.push(val);
                        }
                        renderIndicacoesSelecionadas();
                        this.value = '';
                    }
                }
            });
        }

        // Modal: botões
        const catBtnSalvar = document.getElementById('catBtnSalvar');
        if (catBtnSalvar) catBtnSalvar.addEventListener('click', salvarCategorizacao);

        const catBtnDepois = document.getElementById('catBtnDepois');
        if (catBtnDepois) {
            catBtnDepois.addEventListener('click', function() {
                if (catModalInstance) catModalInstance.hide();
                pendingCategorizeCallback(false);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', _initBindings);
    } else {
        _initBindings();
    }

    // Expor funções globais para o código existente
    window._openCategorizarModal = openCategorizarModal;
    window._loadTaxonomia = loadTaxonomia;
})();

// Inicializar ambas as abas especializadas
document.addEventListener('DOMContentLoaded', function() {
    initSpecialtyTab('antibiotico');
    initSpecialtyTab('isotretinoina');

    // Botões de atalho de posologia (classe .pos-btn)
    document.querySelectorAll('.pos-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var targetId = this.dataset.target;
            var text = this.dataset.text;
            var input = document.getElementById(targetId);
            if (input) {
                input.value = text;
                this.classList.add('pos-btn-pressed');
                setTimeout(function() {
                    btn.classList.remove('pos-btn-pressed');
                }, 200);
            }
        });
    });
});
