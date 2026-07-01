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
    const doctorSelect = document.getElementById('agenda-doctor');
    const dateInput = document.getElementById('agenda-date');
    const maxUploadMb = Number.parseInt(form.dataset.maxUploadMb || '10', 10);
    let analysisResult = null;

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

        const confidenceCell = document.createElement('td');
        confidenceCell.className = 'col-confidence';
        const confidenceBadge = document.createElement('span');
        confidenceBadge.className = `confidence-badge ${confidence < 0.8 ? 'confidence-low' : 'confidence-high'}`;
        confidenceBadge.textContent = `${Math.round(confidence * 100)}%`;
        confidenceCell.appendChild(confidenceBadge);

        [includeCell, timeCell, nameCell, phoneCell, typeCell, procedureCell, notesCell, confidenceCell]
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

        const image = fileInput.files?.[0];
        if (!image) {
            showError('Selecione uma imagem da agenda física.');
            return;
        }
        if (image.size > maxUploadMb * 1024 * 1024) {
            showError(`A imagem excede o limite de ${maxUploadMb} MB.`);
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
}());
