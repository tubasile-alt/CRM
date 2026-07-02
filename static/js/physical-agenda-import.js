(function () {
    console.log('[PAI] v20260701-direct loaded');
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
    const fileInput = document.getElementById('agenda-image');
    const dropZone = document.getElementById('agenda-drop-zone');
    const chooseFileButton = document.getElementById('choose-agenda-file');
    const fileName = document.getElementById('agenda-file-name');
    const imageList = document.getElementById('agenda-image-list');
    const refreshMatchesButton = document.getElementById('refresh-patient-matches');
    const confirmImportButton = document.getElementById('confirm-import-button');
    console.log('[PAI] confirmImportButton found:', confirmImportButton, 'disabled:', confirmImportButton?.disabled);
    const doctorSelect = document.getElementById('agenda-doctor');
    const dateInput = document.getElementById('agenda-date');
    const maxUploadMb = Number.parseInt(form.dataset.maxUploadMb || '10', 10);
    const maxBatchImages = 10;
    let analysisResult = null;
    let imageQueue = [];
    let nextImageId = 1;

    function setLoading(loading, progress = '') {
        analyzeButton.disabled = loading;
        analyzeButton.innerHTML = loading
            ? `<span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>Analisando${progress ? ` ${progress}` : '...'}`
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

    function newImportKey(rowIndex) {
        if (window.crypto?.randomUUID) return window.crypto.randomUUID();
        return `${Date.now()}-${rowIndex}-${Math.random().toString(36).slice(2)}`;
    }

    function onDataChanged() {
        console.log('[PAI] onDataChanged called');
        confirmImportButton.disabled = false;
        console.log('[PAI] confirmImportButton disabled after onDataChanged:', confirmImportButton.disabled);
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

    function renderImageQueue() {
        imageList.replaceChildren();
        dropZone.classList.toggle('has-file', imageQueue.length > 0);
        fileName.textContent = imageQueue.length
            ? `${imageQueue.length} foto(s) adicionada(s). Você ainda pode adicionar mais.`
            : `Até ${maxBatchImages} fotos; JPG, PNG ou WEBP, ${maxUploadMb} MB por imagem.`;

        imageQueue.forEach((entry, index) => {
            const item = document.createElement('div');
            item.className = 'agenda-image-item';
            item.dataset.imageId = String(entry.id);

            const details = document.createElement('div');
            details.className = 'agenda-image-item-name';
            const name = document.createElement('strong');
            name.textContent = entry.file.name;
            const size = document.createElement('small');
            size.textContent = `${(entry.file.size / 1024 / 1024).toFixed(2)} MB · foto ${index + 1}`;
            details.append(name, size);

            const date = document.createElement('input');
            date.type = 'date';
            date.className = 'form-control form-control-sm agenda-image-date';
            date.value = entry.date;
            date.required = true;
            date.setAttribute('aria-label', `Data da foto ${entry.file.name}`);
            date.addEventListener('change', () => {
                entry.date = date.value;
            });

            const remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'btn btn-sm btn-outline-danger';
            remove.title = 'Remover foto';
            remove.setAttribute('aria-label', `Remover ${entry.file.name}`);
            remove.innerHTML = '<i class="bi bi-trash" aria-hidden="true"></i>';
            remove.addEventListener('click', () => {
                imageQueue = imageQueue.filter((candidate) => candidate.id !== entry.id);
                renderImageQueue();
            });

            item.append(details, date, remove);
            imageList.appendChild(item);
        });
    }

    function addImageFiles(files) {
        const incoming = Array.from(files || []);
        if (incoming.length === 0) return false;

        const errors = [];
        incoming.forEach((file) => {
            if (imageQueue.length >= maxBatchImages) {
                errors.push(`O lote aceita até ${maxBatchImages} fotos por vez.`);
                return;
            }
            const validationError = validateImageFile(file);
            if (validationError) {
                errors.push(`${file.name || 'Arquivo'}: ${validationError}`);
                return;
            }
            const duplicate = imageQueue.some((entry) => (
                entry.file.name === file.name
                && entry.file.size === file.size
                && entry.file.lastModified === file.lastModified
            ));
            if (!duplicate) {
                imageQueue.push({ id: nextImageId, file, date: dateInput.value });
                nextImageId += 1;
            }
        });

        renderImageQueue();
        if (errors.length) {
            showError(errors.join(' '));
        } else {
            clearError();
        }
        fileInput.value = '';
        return imageQueue.length > 0;
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
        row.dataset.importKey = item.idempotency_key || newImportKey(rowIndex);
        if (confidence < 0.8) row.classList.add('low-confidence-row');

        const includeCell = document.createElement('td');
        includeCell.className = 'col-include';
        const include = document.createElement('input');
        include.type = 'checkbox';
        include.className = 'form-check-input agenda-include-row';
        include.checked = Boolean(item.time);
        include.setAttribute('aria-label', `Incluir linha ${rowIndex + 1} na importação`);
        includeCell.appendChild(include);

        const dateCell = document.createElement('td');
        dateCell.className = 'col-date';
        dateCell.appendChild(createField('date', item.agenda_date, 'agenda_date', rowIndex, 'Data da agenda'));

        const timeCell = document.createElement('td');
        const time = createField('time', item.time, 'time', rowIndex, 'Horário');
        time.step = '300';
        timeCell.appendChild(time);

        const nameCell = document.createElement('td');
        nameCell.appendChild(createField('text', item.patient_name, 'patient_name', rowIndex, 'Nome do paciente'));

        const phoneCell = document.createElement('td');
        const phone = createField('tel', item.phone, 'phone', rowIndex, 'Telefone');
        phone.inputMode = 'numeric';
        phoneCell.appendChild(phone);

        const cpfCell = document.createElement('td');
        const cpf = createField('text', item.cpf, 'cpf', rowIndex, 'CPF');
        cpf.inputMode = 'numeric';
        cpfCell.appendChild(cpf);

        const codeCell = document.createElement('td');
        const patientCode = createField('number', item.patient_code, 'patient_code', rowIndex, 'Código do paciente');
        patientCode.min = '1';
        codeCell.appendChild(patientCode);

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

        const validationCell = document.createElement('td');
        validationCell.className = 'col-validation import-validation-cell text-muted';
        validationCell.textContent = 'Aguardando paciente';

        [
            includeCell,
            dateCell,
            timeCell,
            nameCell,
            phoneCell,
            cpfCell,
            codeCell,
            typeCell,
            procedureCell,
            notesCell,
            matchCell,
            validationCell,
        ]
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

    function renderResult(analyses) {
        const successfulAnalyses = Array.isArray(analyses) ? analyses : [analyses];
        const items = successfulAnalyses.flatMap((analysis) => (
            (Array.isArray(analysis.items) ? analysis.items : []).map((item) => ({
                ...item,
                agenda_date: analysis.agenda_date,
            }))
        ));
        const warnings = successfulAnalyses.flatMap((analysis) => (
            (analysis.warnings || []).map((warning) => `${analysis.agenda_date}: ${warning}`)
        ));
        const agendaDates = [...new Set(successfulAnalyses.map((analysis) => analysis.agenda_date))];
        analysisResult = {
            doctor_id: successfulAnalyses[0]?.doctor_id,
            doctor_name: successfulAnalyses[0]?.doctor_name,
            items,
        };
        confirmImportButton.disabled = false;
        tableBody.replaceChildren();
        items.forEach((item, index) => tableBody.appendChild(renderItem(item, index)));

        summary.textContent = `${agendaDates.length} dia(s) · ${analysisResult.doctor_name} · ${items.length} item(ns)`;
        renderWarnings(warnings);
        tableWrapper.hidden = items.length === 0;
        emptyState.hidden = items.length !== 0;
        resultSection.hidden = false;
        loadPatientSuggestions();
    }

    function rowValue(row, field) {
        return row.querySelector(`[data-field="${field}"]`)?.value.trim() || '';
    }

    function setValidationState(row, text, className = 'text-muted') {
        const cell = row.querySelector('.import-validation-cell');
        cell.className = `col-validation import-validation-cell ${className}`;
        cell.textContent = text;
    }

    function markMatchedPatient(row, patient, status) {
        const cell = row.querySelector('.patient-match-cell');
        row.dataset.patientId = String(patient.patient_id);
        row.dataset.patientStatus = status;
        setValidationState(
            row,
            status === 'ativo' ? 'Paciente ativo confirmado \u2713' : 'Provisório confirmado \u2713',
            status === 'ativo' ? 'import-validation-ready' : 'text-warning',
        );
        onDataChanged();
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
        setValidationState(row, 'Aguardando seleção');

        if (!Array.isArray(suggestions) || suggestions.length === 0) {
            const empty = document.createElement('span');
            empty.className = 'text-muted';
            empty.textContent = 'Nenhum paciente ativo encontrado.';
            cell.appendChild(empty);
            createProvisionalButton(row, cell);
            setValidationState(row, 'Criará provisório', 'text-warning');
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
                delete row.dataset.patientId;
                delete row.dataset.patientStatus;
                setValidationState(row, 'Criará provisório', 'text-warning');
                createProvisionalButton(row, actionArea);
                return;
            }
            const option = select.options[select.selectedIndex];
            if (!option?.dataset.patient) {
                delete row.dataset.patientId;
                delete row.dataset.patientStatus;
                setValidationState(row, 'Aguardando seleção');
                return;
            }
            const patient = JSON.parse(option.dataset.patient);
            row.dataset.patientId = String(patient.patient_id);
            row.dataset.patientStatus = 'ativo';
            setValidationState(row, 'Paciente ativo confirmado \u2713', 'import-validation-ready');
            onDataChanged();
            const meta = document.createElement('span');
            meta.className = 'patient-match-meta';
            const contact = patient.patient_phone || 'sem telefone';
            const link = patient.linked_to_doctor ? `cód. ${patient.patient_code || '-'}` : 'sem vínculo com este médico';
            const cpf = patient.patient_cpf_suffix ? `CPF final ${patient.patient_cpf_suffix}` : 'CPF não informado';
            meta.textContent = `${contact} · ${cpf} · ${link}`;
            actionArea.appendChild(meta);
        });
        cell.append(select, actionArea);

        const best = suggestions[0];
        const second = suggestions[1];
        if (best.score >= 0.9 && (!second || second.score < best.score)) {
            select.value = String(best.patient_id);
            select.dispatchEvent(new Event('change'));
        }
    }

    async function loadPatientSuggestions() {
        if (!analysisResult) return;
        clearError();
        onDataChanged();
        refreshMatchesButton.disabled = true;
        const rows = Array.from(tableBody.querySelectorAll('tr[data-row-index]'));
        rows.forEach((row) => {
            const cell = row.querySelector('.patient-match-cell');
            cell.textContent = 'Buscando pacientes ativos...';
            setValidationState(row, 'Buscando paciente...');
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
                        cpf: rowValue(row, 'cpf'),
                        patient_code: rowValue(row, 'patient_code'),
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
                setValidationState(row, 'Validação indisponível', 'import-validation-error');
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
            .filter((row) => (
                row.querySelector('.agenda-include-row')?.checked
                && row.dataset.imported !== 'true'
            ))
            .map((row) => {
                const index = Number.parseInt(row.dataset.rowIndex, 10);
                const original = analysisResult.items[index];
                const value = (field) => {
                    const text = row.querySelector(`[data-field="${field}"]`)?.value.trim() || '';
                    return text || null;
                };
                return {
                    agenda_date: value('agenda_date'),
                    time: value('time'),
                    patient_name: value('patient_name'),
                    phone: value('phone'),
                    cpf: value('cpf'),
                    patient_code: value('patient_code'),
                    appointment_type: value('appointment_type'),
                    procedure: value('procedure'),
                    duration_minutes: 5,
                    notes: value('notes'),
                    patient_id: row.dataset.patientId ? Number.parseInt(row.dataset.patientId, 10) : null,
                    patient_status: row.dataset.patientStatus || null,
                    idempotency_key: row.dataset.importKey,
                    confidence: original.confidence,
                    raw_text: original.raw_text,
                };
            });
    }

    function selectedImportRows() {
        return Array.from(tableBody.querySelectorAll('tr[data-row-index]'))
            .filter((row) => row.querySelector('.agenda-include-row')?.checked && row.dataset.imported !== 'true');
    }

    async function confirmAppointmentImport() {
        console.log('[PAI] confirmAppointmentImport() clicked');
        clearError();
        const rows = selectedImportRows();
        const items = editedItems();
        console.log('[PAI] rows:', rows.length, 'items:', items.length);
        if (items.length === 0) {
            showError('Selecione ao menos uma linha para importar.');
            return;
        }
        if (!window.confirm(`Criar ${items.length} agendamento(s) na agenda do médico selecionado? Pacientes sem match serão criados como provisórios automaticamente.`)) {
            console.log('[PAI] user cancelled');
            return;
        }

        confirmImportButton.disabled = true;
        try {
            const response = await fetch('/api/agenda-fisica/importar', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.getCSRFToken?.() || '',
                },
                body: JSON.stringify({
                    doctor_id: doctorSelect.value,
                    confirmed: true,
                    items,
                }),
            });
            const data = await response.json().catch(() => null);
            if (!response.ok || !data?.success) {
                throw new Error(data?.error || 'Não foi possível criar os agendamentos.');
            }

            rows.forEach((row, index) => {
                row.dataset.imported = 'true';
                row.querySelectorAll('input, textarea, select, button').forEach((control) => {
                    control.disabled = true;
                });
                const cell = row.querySelector('.import-validation-cell');
                const apt = data.appointments?.[index];
                const timeField = row.querySelector('[data-field="time"]');
                if (apt?.start && timeField) {
                    timeField.value = apt.start.slice(11, 16);
                }
                if (apt?.patient_resolution === 'ativo_encontrado') {
                    cell.className = 'col-validation import-validation-cell import-validation-ready';
                    cell.textContent = 'Ativo \u2713';
                } else if (apt?.patient_resolution === 'provisorio_existente') {
                    cell.className = 'col-validation import-validation-cell text-warning';
                    cell.textContent = 'Prov. existente \u2713';
                } else {
                    cell.className = 'col-validation import-validation-cell text-warning';
                    cell.textContent = 'Provisório \u2713';
                }
            });
            if (window.showAlert) {
                window.showAlert(`${data.created_count} agendamento(s) criado(s) com sucesso.`, 'success');
            }
        } catch (error) {
            showError(error.message || 'Não foi possível criar os agendamentos.');
        } finally {
            confirmImportButton.disabled = false;
        }
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearError();

        if (imageQueue.length === 0) {
            showError('Adicione pelo menos uma imagem da agenda física.');
            return;
        }
        if (!doctorSelect.value) {
            showError('Selecione o médico responsável.');
            return;
        }
        if (imageQueue.some((entry) => !entry.date)) {
            showError('Informe a data de todas as fotos antes de analisar.');
            return;
        }

        setLoading(true);
        resultSection.hidden = true;
        const analyses = [];
        const failures = [];
        try {
            for (let index = 0; index < imageQueue.length; index += 1) {
                const entry = imageQueue[index];
                setLoading(true, `${index + 1}/${imageQueue.length}`);
                const formData = new FormData();
                formData.append('date', entry.date);
                formData.append('doctor_id', doctorSelect.value);
                formData.append('image', entry.file, entry.file.name);

                try {
                    const response = await fetch('/api/agenda-fisica/analisar', {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers: { 'X-CSRFToken': window.getCSRFToken?.() || '' },
                        body: formData,
                    });
                    const data = await response.json().catch(() => null);
                    if (!response.ok || !data?.success) {
                        throw new Error(data?.error || 'Não foi possível analisar esta imagem.');
                    }
                    analyses.push(data);
                } catch (error) {
                    failures.push(`${entry.file.name}: ${error.message || 'falha na análise'}`);
                }
            }
            if (analyses.length > 0) {
                renderResult(analyses);
            }
            if (failures.length > 0) {
                showError(`Algumas fotos não foram analisadas. ${failures.join(' ')}`);
            } else if (analyses.length === 0) {
                showError('Não foi possível analisar as imagens.');
            }
        } finally {
            setLoading(false);
        }
    });

    refreshMatchesButton.addEventListener('click', loadPatientSuggestions);
    console.log('[PAI] refreshMatchesButton listener registered');
    tableBody.addEventListener('input', (event) => {
        if (!event.target.matches('input, textarea, select')) return;
        const row = event.target.closest('tr[data-row-index]');
        const identityFields = ['patient_name', 'phone', 'cpf', 'patient_code'];
        if (row && identityFields.includes(event.target.dataset.field)) {
            delete row.dataset.patientId;
            delete row.dataset.patientStatus;
            const matchCell = row.querySelector('.patient-match-cell');
            matchCell.className = 'col-match patient-match-cell text-muted';
            matchCell.textContent = 'Atualize as sugestões';
            setValidationState(row, 'Revalidar paciente', 'text-warning');
        }
        if (row && event.target.dataset.field === 'time') {
            row.querySelector('.agenda-include-row').checked = Boolean(event.target.value);
        }
        onDataChanged();
    });
    fileInput.addEventListener('change', () => addImageFiles(fileInput.files));
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
        addImageFiles(event.dataTransfer?.files);
    });
    renderImageQueue();
}());
