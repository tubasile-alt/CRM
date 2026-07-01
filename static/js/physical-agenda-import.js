(function () {
    const form = document.getElementById('physical-agenda-form');
    if (!form) return;

    const analyzeButton = document.getElementById('analyze-agenda-button');
    const errorBox = document.getElementById('analysis-error');
    const resultSection = document.getElementById('analysis-result');
    const summary = document.getElementById('analysis-summary');
    const warningsBox = document.getElementById('analysis-warnings');
    const tableWrapper = document.getElementById('analysis-table-wrapper');
    const tableBody = document.getElementById('analysis-items');
    const emptyState = document.getElementById('empty-analysis');
    const copyButton = document.getElementById('copy-json-button');
    const downloadButton = document.getElementById('download-json-button');
    const fileInput = document.getElementById('agenda-image');
    const dropZone = document.getElementById('agenda-drop-zone');
    const chooseFileButton = document.getElementById('choose-agenda-file');
    const fileName = document.getElementById('agenda-file-name');
    const refreshMatchesButton = document.getElementById('refresh-patient-matches');
    const doctorSelect = document.getElementById('agenda-doctor');
    const dateInput = document.getElementById('agenda-date');
    const maxUploadMb = Number.parseInt(form.dataset.maxUploadMb || '10', 10);
    let analysisResult = null;
    let selectedImageFile = null;

    function setLoading(loading) {
        analyzeButton.disabled = loading;
        analyzeButton.innerHTML = loading
            ? '<span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>Analisando...'
            : '<i class="bi bi-stars me-1"></i>Analisar agenda';
    }

    function showError(message) {
        errorBox.textContent = message;
        errorBox.hidden = false;
    }

    function clearError() {
        errorBox.textContent = '';
        errorBox.hidden = true;
    }

    function validateImageFile(file) {
        if (!file) return 'Selecione uma imagem da agenda física.';
        const extension = file.name.includes('.') ? file.name.split('.').pop().toLowerCase() : '';
        const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp'];
        const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/webp'];
        if (!allowedExtensions.includes(extension) || (file.type && !allowedMimeTypes.includes(file.type))) {
            return 'Formato inválido. Envie uma imagem JPG, PNG ou WEBP.';
        }
        if (file.size > maxUploadMb * 1024 * 1024) {
            return `A imagem excede o limite de ${maxUploadMb} MB.`;
        }
        return null;
    }

    function selectImageFile(file) {
        const validationError = validateImageFile(file);
        if (validationError) {
            selectedImageFile = null;
            dropZone.classList.remove('has-file');
            showError(validationError);
            return false;
        }

        clearError();
        selectedImageFile = file;
        dropZone.classList.add('has-file');
        fileName.textContent = `${file.name} · ${(file.size / 1024 / 1024).toFixed(2)} MB`;
        return true;
    }

    function createField(type, value, field, rowIndex, label) {
        const input = document.createElement('input');
        input.type = type;
        input.className = 'form-control form-control-sm';
        input.value = value || '';
        input.dataset.field = field;
        input.dataset.rowIndex = String(rowIndex);
        input.setAttribute('aria-label', label);
        return input;
    }

    function renderItem(item, rowIndex) {
        const row = document.createElement('tr');
        const confidence = Number(item.confidence || 0);
        row.dataset.rowIndex = String(rowIndex);
        if (confidence < 0.8) row.classList.add('low-confidence-row');

        const includeCell = document.createElement('td');
        includeCell.className = 'col-include';
        const include = document.createElement('input');
        include.type = 'checkbox';
        include.className = 'form-check-input agenda-include-row';
        include.checked = true;
        include.setAttribute('aria-label', `Incluir linha ${rowIndex + 1} no JSON`);
        includeCell.appendChild(include);

        const timeCell = document.createElement('td');
        timeCell.appendChild(createField('time', item.time, 'time', rowIndex, 'Horário'));

        const nameCell = document.createElement('td');
        nameCell.appendChild(createField('text', item.patient_name, 'patient_name', rowIndex, 'Nome do paciente'));

        const phoneCell = document.createElement('td');
        const phone = createField('tel', item.phone, 'phone', rowIndex, 'Telefone');
        phone.inputMode = 'numeric';
        phoneCell.appendChild(phone);

        const typeCell = document.createElement('td');
        typeCell.appendChild(createField('text', item.appointment_type, 'appointment_type', rowIndex, 'Tipo'));

        const procedureCell = document.createElement('td');
        procedureCell.appendChild(createField('text', item.procedure, 'procedure', rowIndex, 'Procedimento'));

        const notesCell = document.createElement('td');
        const notes = document.createElement('textarea');
        notes.className = 'form-control form-control-sm';
        notes.value = item.notes || '';
        notes.dataset.field = 'notes';
        notes.dataset.rowIndex = String(rowIndex);
        notes.setAttribute('aria-label', 'Observações');
        notesCell.appendChild(notes);

        const matchCell = document.createElement('td');
        matchCell.className = 'col-match patient-match-cell';
        matchCell.dataset.patientMatchIndex = String(rowIndex);
        matchCell.textContent = 'Aguardando sugestões...';

        const confidenceCell = document.createElement('td');
        confidenceCell.className = 'col-confidence';
        const confidenceBadge = document.createElement('span');
        confidenceBadge.className = `confidence-badge ${confidence < 0.8 ? 'confidence-low' : 'confidence-high'}`;
        confidenceBadge.textContent = `${Math.round(confidence * 100)}%`;
        confidenceCell.appendChild(confidenceBadge);

        [includeCell, timeCell, nameCell, phoneCell, typeCell, procedureCell, notesCell, matchCell, confidenceCell]
            .forEach((cell) => row.appendChild(cell));
        return row;
    }

    function renderWarnings(warnings) {
        warningsBox.replaceChildren();
        if (!Array.isArray(warnings) || warnings.length === 0) {
            warningsBox.hidden = true;
            return;
        }

        const list = document.createElement('ul');
        list.className = 'mb-0';
        warnings.forEach((warning) => {
            const item = document.createElement('li');
            item.textContent = warning;
            list.appendChild(item);
        });
        warningsBox.appendChild(list);
        warningsBox.hidden = false;
    }

    function renderResult(data) {
        analysisResult = data;
        tableBody.replaceChildren();
        const items = Array.isArray(data.items) ? data.items : [];
        items.forEach((item, index) => tableBody.appendChild(renderItem(item, index)));

        summary.textContent = `${data.agenda_date} · ${data.doctor_name} · ${items.length} item(ns)`;
        renderWarnings(data.warnings);
        tableWrapper.hidden = items.length === 0;
        emptyState.hidden = items.length !== 0;
        copyButton.disabled = items.length === 0;
        downloadButton.disabled = items.length === 0;
        resultSection.hidden = false;
        loadPatientSuggestions();
    }

    function rowValue(row, field) {
        return row.querySelector(`[data-field="${field}"]`)?.value.trim() || '';
    }

    function markMatchedPatient(row, patient, status) {
        const cell = row.querySelector('.patient-match-cell');
        row.dataset.patientId = String(patient.patient_id);
        row.dataset.patientStatus = status;
        cell.replaceChildren();

        const badge = document.createElement('span');
        badge.className = `badge ${status === 'ativo' ? 'text-bg-success' : 'text-bg-warning'}`;
        badge.textContent = status === 'ativo' ? 'Paciente ativo selecionado' : 'Cadastro provisório';
        const name = document.createElement('span');
        name.className = 'patient-match-meta';
        name.textContent = patient.patient_name;
        const changeButton = document.createElement('button');
        changeButton.type = 'button';
        changeButton.className = 'btn btn-link btn-sm p-0 mt-1';
        changeButton.textContent = 'Alterar sugestão';
        changeButton.addEventListener('click', () => loadPatientSuggestions());
        cell.append(badge, name, changeButton);
    }

    function createProvisionalButton(row, container) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-sm btn-outline-warning mt-1';
        button.innerHTML = '<i class="bi bi-person-plus me-1"></i>Criar provisório';
        button.addEventListener('click', async () => {
            const patientName = rowValue(row, 'patient_name');
            const phone = rowValue(row, 'phone');
            if (!patientName) {
                showError('Informe o nome antes de criar o cadastro provisório.');
                return;
            }
            if (!window.confirm(`Criar cadastro provisório para "${patientName}"? Nenhum agendamento será criado.`)) {
                return;
            }

            button.disabled = true;
            try {
                const response = await fetch('/api/agenda-fisica/pacientes-provisorios', {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.getCSRFToken?.() || '',
                    },
                    body: JSON.stringify({
                        doctor_id: doctorSelect.value,
                        patient_name: patientName,
                        phone,
                    }),
                });
                const data = await response.json().catch(() => null);
                if (response.status === 409 && data?.existing_provisional) {
                    markMatchedPatient(row, data.existing_provisional, 'provisorio');
                    if (window.showAlert) window.showAlert('Cadastro provisório existente selecionado.', 'warning');
                    return;
                }
                if (response.status === 409 && Array.isArray(data?.suggestions)) {
                    renderPatientSuggestions(row, data.suggestions);
                    showError(data.error);
                    return;
                }
                if (!response.ok || !data?.success) {
                    throw new Error(data?.error || 'Não foi possível criar o cadastro provisório.');
                }
                markMatchedPatient(row, data.patient, 'provisorio');
                if (window.showAlert) window.showAlert('Cadastro provisório criado. Nenhum agendamento foi gerado.', 'success');
            } catch (error) {
                showError(error.message || 'Não foi possível criar o cadastro provisório.');
                button.disabled = false;
            }
        });
        container.appendChild(button);
    }

    function renderPatientSuggestions(row, suggestions) {
        const cell = row.querySelector('.patient-match-cell');
        cell.replaceChildren();
        delete row.dataset.patientId;
        delete row.dataset.patientStatus;

        if (!Array.isArray(suggestions) || suggestions.length === 0) {
            const empty = document.createElement('span');
            empty.className = 'text-muted';
            empty.textContent = 'Nenhum paciente ativo encontrado.';
            cell.appendChild(empty);
            createProvisionalButton(row, cell);
            return;
        }

        const select = document.createElement('select');
        select.className = 'form-select form-select-sm';
        select.setAttribute('aria-label', 'Sugestão de paciente ativo');
        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = 'Selecione um paciente ativo';
        select.appendChild(placeholder);

        suggestions.forEach((suggestion) => {
            const option = document.createElement('option');
            option.value = String(suggestion.patient_id);
            option.textContent = `${suggestion.patient_name} · ${Math.round(suggestion.score * 100)}%`;
            option.dataset.patient = JSON.stringify(suggestion);
            select.appendChild(option);
        });
        const newOption = document.createElement('option');
        newOption.value = '__new__';
        newOption.textContent = 'Nenhum corresponde';
        select.appendChild(newOption);

        const actionArea = document.createElement('div');
        select.addEventListener('change', () => {
            actionArea.replaceChildren();
            if (select.value === '__new__') {
                createProvisionalButton(row, actionArea);
                return;
            }
            const option = select.options[select.selectedIndex];
            if (!option?.dataset.patient) {
                delete row.dataset.patientId;
                delete row.dataset.patientStatus;
                return;
            }
            const patient = JSON.parse(option.dataset.patient);
            row.dataset.patientId = String(patient.patient_id);
            row.dataset.patientStatus = 'ativo';
            const meta = document.createElement('span');
            meta.className = 'patient-match-meta';
            const contact = patient.patient_phone || 'sem telefone';
            const link = patient.linked_to_doctor ? `cód. ${patient.patient_code || '-'}` : 'sem vínculo com este médico';
            meta.textContent = `${contact} · ${link}`;
            actionArea.appendChild(meta);
        });
        cell.append(select, actionArea);
    }

    async function loadPatientSuggestions() {
        if (!analysisResult) return;
        clearError();
        refreshMatchesButton.disabled = true;
        const rows = Array.from(tableBody.querySelectorAll('tr[data-row-index]'));
        rows.forEach((row) => {
            const cell = row.querySelector('.patient-match-cell');
            cell.textContent = 'Buscando pacientes ativos...';
        });

        try {
            const response = await fetch('/api/agenda-fisica/sugerir-pacientes', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.getCSRFToken?.() || '',
                },
                body: JSON.stringify({
                    doctor_id: doctorSelect.value,
                    items: rows.map((row) => ({
                        patient_name: rowValue(row, 'patient_name'),
                        phone: rowValue(row, 'phone'),
                    })),
                }),
            });
            const data = await response.json().catch(() => null);
            if (!response.ok || !data?.success) {
                throw new Error(data?.error || 'Não foi possível buscar pacientes ativos.');
            }
            const suggestionsByRow = new Map(
                data.matches.map((match) => [Number(match.row_index), match.suggestions])
            );
            rows.forEach((row) => {
                const index = Number.parseInt(row.dataset.rowIndex, 10);
                renderPatientSuggestions(row, suggestionsByRow.get(index) || []);
            });
        } catch (error) {
            rows.forEach((row) => {
                row.querySelector('.patient-match-cell').textContent = 'Sugestões indisponíveis.';
            });
            showError(error.message || 'Não foi possível buscar pacientes ativos.');
        } finally {
            refreshMatchesButton.disabled = false;
        }
    }

    function editedItems() {
        if (!analysisResult) return [];
        const rows = Array.from(tableBody.querySelectorAll('tr[data-row-index]'));
        return rows
            .filter((row) => row.querySelector('.agenda-include-row')?.checked)
            .map((row) => {
                const index = Number.parseInt(row.dataset.rowIndex, 10);
                const original = analysisResult.items[index];
                const value = (field) => {
                    const text = row.querySelector(`[data-field="${field}"]`)?.value.trim() || '';
                    return text || null;
                };
                return {
                    time: value('time'),
                    patient_name: value('patient_name'),
                    phone: value('phone'),
                    appointment_type: value('appointment_type'),
                    procedure: value('procedure'),
                    notes: value('notes'),
                    confidence: original.confidence,
                    raw_text: original.raw_text,
                };
            });
    }

    function exportPayload() {
        return {
            success: true,
            agenda_date: analysisResult.agenda_date,
            doctor_id: analysisResult.doctor_id,
            doctor_name: analysisResult.doctor_name,
            items: editedItems(),
            warnings: analysisResult.warnings || [],
        };
    }

    async function copyJson() {
        const json = JSON.stringify(exportPayload(), null, 2);
        try {
            await navigator.clipboard.writeText(json);
        } catch (error) {
            const textarea = document.createElement('textarea');
            textarea.value = json;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            textarea.remove();
        }
        if (window.showAlert) window.showAlert('JSON copiado para a área de transferência.', 'success');
    }

    function downloadJson() {
        const json = JSON.stringify(exportPayload(), null, 2);
        const blob = new Blob([json], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `agenda-fisica-${analysisResult.agenda_date}.json`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearError();

        const image = selectedImageFile || fileInput.files?.[0];
        if (!image) {
            showError('Selecione uma imagem da agenda física.');
            return;
        }
        const validationError = validateImageFile(image);
        if (validationError) {
            showError(validationError);
            return;
        }

        const formData = new FormData();
        formData.append('date', dateInput.value);
        formData.append('doctor_id', doctorSelect.value);
        formData.append('image', image, image.name);

        setLoading(true);
        resultSection.hidden = true;
        try {
            const response = await fetch('/api/agenda-fisica/analisar', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'X-CSRFToken': window.getCSRFToken?.() || '' },
                body: formData,
            });
            const data = await response.json().catch(() => null);
            if (!response.ok || !data?.success) {
                throw new Error(data?.error || 'Não foi possível analisar a imagem.');
            }
            renderResult(data);
        } catch (error) {
            showError(error.message || 'Não foi possível analisar a imagem.');
        } finally {
            setLoading(false);
        }
    });

    copyButton.addEventListener('click', copyJson);
    downloadButton.addEventListener('click', downloadJson);
    refreshMatchesButton.addEventListener('click', loadPatientSuggestions);
    fileInput.addEventListener('change', () => selectImageFile(fileInput.files?.[0]));
    chooseFileButton.addEventListener('click', (event) => {
        event.stopPropagation();
        fileInput.click();
    });
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            fileInput.click();
        }
    });
    ['dragenter', 'dragover'].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            event.stopPropagation();
            dropZone.classList.add('is-dragover');
        });
    });
    ['dragleave', 'drop'].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            event.stopPropagation();
            dropZone.classList.remove('is-dragover');
        });
    });
    dropZone.addEventListener('drop', (event) => {
        selectImageFile(event.dataTransfer?.files?.[0]);
    });
}());
