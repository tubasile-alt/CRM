(function() {
    let appointmentsList = [];
    let waitingRoomData = [];
    let calendar = null;
    let selectedDate = new Date();
    let currentDoctorFilter = null;
    let currentView = 'day';
    let currentEvent = null;
    let webcamStream = null;

    window.parseLocalDateTime = function(isoString) {
        if (!isoString) return null;
        // Se já for um objeto Date, retorna ele mesmo
        if (isoString instanceof Date) return isoString;
        
        // Remove fuso horário para tratar como hora local literal do banco
        const cleanString = isoString.replace(/[+-]\d{2}:\d{2}$/, '').replace('Z', '');
        const parts = cleanString.split('T');
        if (parts.length < 2) return new Date(cleanString);
        
        const [datePart, timePart] = parts;
        const [year, month, day] = datePart.split('-').map(Number);
        const [hours, minutes, seconds] = timePart.split(':').map(Number);
        
        return new Date(year, month - 1, day, hours, minutes || 0, seconds || 0);
    };

    window.getCSRFToken = function() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    };

    window.showAlert = function(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        document.body.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 3000);
    };

    document.addEventListener('DOMContentLoaded', function() {
        if (window.isDoctor && window.currentDoctorId) {
            currentDoctorFilter = parseInt(window.currentDoctorId);
        } else {
            // Se for secretária, tenta recuperar o último médico filtrado
            const savedFilter = localStorage.getItem('agenda_doctor_filter');
            if (savedFilter) {
                currentDoctorFilter = parseInt(savedFilter);
                // Aguarda um pouco para os botões renderizarem e marca o ativo
                setTimeout(() => {
                    const btn = document.getElementById(`btn-doc-${currentDoctorFilter}`);
                    if (btn) filterByDoctor(currentDoctorFilter, btn);
                }, 100);
            }
        }
        
        initializeDayView();
        initializeMonthCalendar();
        loadAppointments();
        updateWaitingCounter();
        setInterval(updateWaitingCounter, 30000);
        renderMiniCalendar();
        setupPatientAutocomplete();
        startWaitingRoomUpdates();
        startWaitingClock();
        setupWebcamHandlers();

        // Polling automático: atualiza apenas blocos com status alterado, a cada 60 segundos.
        // Ignora quando há um modal aberto para não interromper interações em curso.
        setInterval(_autoRefreshAppointments, 60000);

        // Atualiza imediatamente ao voltar para a aba após > 30 segundos em background
        let _hiddenSince = null;
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'hidden') {
                _hiddenSince = Date.now();
            } else if (document.visibilityState === 'visible') {
                const away = _hiddenSince ? (Date.now() - _hiddenSince) : 0;
                if (away > 30000) {
                    _autoRefreshAppointments();
                }
                _hiddenSince = null;
            }
        });

        // Limpar campos de formulário automaticamente quando o modal de novo agendamento abrir
        const newModalEl = document.getElementById('newAppointmentModal');
        if (newModalEl) {
            newModalEl.addEventListener('shown.bs.modal', function() {
                const idsToClear = ['selectedPatientId', 'patientPhotoData', 'patientCode', 'patientCPF', 'patientBirthDate', 'patientPhone', 'patientAddress', 'patientCity', 'patientMotherName', 'patientIndicationSource', 'patientOccupation'];
                idsToClear.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.value = '';
                });
            });
        }
    });

    function setupPatientAutocomplete() {
        const patientInput = document.getElementById('patientName');
        const suggestionsDiv = document.getElementById('patientSuggestions');
        if (!patientInput || !suggestionsDiv) return;

        patientInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length < 2) {
                suggestionsDiv.style.display = 'none';
                return;
            }

            fetch(`/api/doctor-patients/search?q=${encodeURIComponent(query)}`)
                .then(r => r.json())
                .then(results => {
                    suggestionsDiv.innerHTML = '';
                    if (!Array.isArray(results) || results.length === 0) {
                        // Fallback para busca simples se não houver vínculo dp
                        return fetch(`/api/patients/search?q=${encodeURIComponent(query)}`)
                            .then(r2 => r2.json())
                            .then(patients => {
                                if (!Array.isArray(patients) || patients.length === 0) {
                                    suggestionsDiv.style.display = 'none';
                                    return;
                                }
                                patients.forEach(patient => {
                                    const div = document.createElement('div');
                                    div.className = 'p-2 border-bottom cursor-pointer hover-bg-light';
                                    div.style.cursor = 'pointer';
                                    div.textContent = patient.name;
                                    div.onclick = () => selectPatient({
                                        id: patient.id, name: patient.name,
                                        dp_id: null, patient_code: null,
                                        cpf: patient.cpf, birth_date: patient.birth_date,
                                        phone: patient.phone, address: patient.address,
                                        city: patient.city, mother_name: patient.mother_name,
                                        indication_source: patient.indication_source,
                                        occupation: patient.occupation,
                                        patient_type: patient.patient_type
                                    });
                                    suggestionsDiv.appendChild(div);
                                });
                                suggestionsDiv.style.display = 'block';
                            });
                    }
                    results.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'p-2 border-bottom cursor-pointer hover-bg-light';
                        div.style.cursor = 'pointer';
                        const roleLabel = item.doctor_role === 'CP' ? 'CP' : 'DERM';
                        div.innerHTML = `<span class="fw-semibold">${item.patient_name}</span> <span class="text-muted small">— Dr(a). ${item.doctor_name} (${roleLabel}) — Cód. ${item.patient_code}</span>`;
                        div.onclick = () => selectPatient({
                            id: item.patient_id,
                            name: item.patient_name,
                            dp_id: item.dp_id,
                            patient_code: item.patient_code,
                            phone: item.patient_phone,
                            doctor_role: item.doctor_role
                        });
                        suggestionsDiv.appendChild(div);
                    });
                    suggestionsDiv.style.display = 'block';
                })
                .catch(err => console.error('Erro autocomplete:', err));
        });

        document.addEventListener('click', (e) => {
            if (e.target !== patientInput && !suggestionsDiv.contains(e.target)) {
                suggestionsDiv.style.display = 'none';
            }
        });
    }

    window.selectPatient = function(patient) {
        document.getElementById('selectedPatientId').value = patient.id;
        document.getElementById('patientName').value = patient.name;
        document.getElementById('patientCode').value = patient.patient_code || '';
        if (document.getElementById('patientCPF')) document.getElementById('patientCPF').value = patient.cpf || '';
        if (document.getElementById('patientBirthDate')) document.getElementById('patientBirthDate').value = patient.birth_date || '';
        if (document.getElementById('patientPhone')) document.getElementById('patientPhone').value = patient.phone || '';
        if (document.getElementById('patientAddress')) document.getElementById('patientAddress').value = patient.address || '';
        if (document.getElementById('patientCity')) document.getElementById('patientCity').value = patient.city || '';
        if (document.getElementById('patientMotherName')) document.getElementById('patientMotherName').value = patient.mother_name || '';
        if (document.getElementById('patientIndicationSource')) document.getElementById('patientIndicationSource').value = patient.indication_source || '';
        if (document.getElementById('patientOccupation')) document.getElementById('patientOccupation').value = patient.occupation || '';
        if (document.getElementById('patientType')) document.getElementById('patientType').value = patient.patient_type || 'particular';
        if (patient.dp_id) {
            const dpInput = document.getElementById('selectedDpId');
            if (dpInput) dpInput.value = patient.dp_id;
        }
        document.getElementById('patientSuggestions').style.display = 'none';
    };

    async function startWebcam(videoId, placeholderId, startBtnId, captureBtnId) {
        const video = document.getElementById(videoId);
        const placeholder = document.getElementById(placeholderId);
        const startBtn = document.getElementById(startBtnId);
        const captureBtn = document.getElementById(captureBtnId);

        try {
            if (webcamStream) {
                webcamStream.getTracks().forEach(track => track.stop());
            }
            // Especificar explicitamente que queremos video, não arquivos
            webcamStream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: "user",
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }, 
                audio: false 
            });
            
            if (video) {
                video.srcObject = webcamStream;
                video.onloadedmetadata = () => {
                    video.play();
                    video.style.display = 'block';
                };
            }
            if (placeholder) placeholder.style.display = 'none';
            if (startBtn) startBtn.style.display = 'none';
            if (captureBtn) captureBtn.style.display = 'inline-block';
        } catch (err) {
            console.error("Erro webcam:", err);
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                showAlert("Permissão de câmera negada. Por favor, habilite o acesso no navegador.", "danger");
            } else {
                showAlert("Não foi possível acessar a câmera. Verifique se ela está conectada.", "danger");
            }
        }
    }

    function capturePhoto(videoId, canvasId, previewId, captureBtnId, retakeBtnId, photoDataId) {
        const video = document.getElementById(videoId);
        const canvas = document.getElementById(canvasId);
        const preview = document.getElementById(previewId);
        const captureBtn = document.getElementById(captureBtnId);
        const retakeBtn = document.getElementById(retakeBtnId);
        const photoData = document.getElementById(photoDataId);

        if (!video || !canvas) return;
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const data = canvas.toDataURL('image/jpeg');
        
        if (photoData) photoData.value = data;
        if (preview) {
            preview.src = data;
            preview.style.display = 'block';
        }
        video.style.display = 'none';
        if (captureBtn) captureBtn.style.display = 'none';
        if (retakeBtn) retakeBtn.style.display = 'inline-block';
        
        if (webcamStream) {
            webcamStream.getTracks().forEach(track => track.stop());
            webcamStream = null;
        }
    }

    function setupWebcamHandlers() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('button');
            if (!btn) return;
            const id = btn.id;
            
            if (id === 'start-webcam-btn') {
                e.preventDefault();
                e.stopPropagation();
                startWebcam('webcam-video', 'webcam-placeholder', 'start-webcam-btn', 'capture-photo-btn');
            }
            if (id === 'capture-photo-btn') {
                e.preventDefault();
                e.stopPropagation();
                capturePhoto('webcam-video', 'photo-canvas', 'patient-photo-preview', 'capture-photo-btn', 'retake-photo-btn', 'patientPhotoData');
            }
            if (id === 'retake-photo-btn') {
                e.preventDefault();
                e.stopPropagation();
                const preview = document.getElementById('patient-photo-preview');
                if (preview) preview.style.display = 'none';
                startWebcam('webcam-video', 'webcam-placeholder', 'start-webcam-btn', 'capture-photo-btn');
            }
            
            // Handlers para o modal de edicao (secretaria)
            if (id === 'edit-start-webcam-btn' || btn.classList.contains('start-webcam-edit')) {
                e.preventDefault();
                e.stopPropagation();
                // Tenta detectar se estamos no modal de edicao de cadastro ou agendamento
                const editVideo = document.getElementById('edit-webcam-video');
                if (editVideo) {
                    startWebcam('edit-webcam-video', 'edit-webcam-placeholder', id, 'edit-capture-photo-btn');
                } else {
                    // Fallback para o modal de novo agendamento
                    startWebcam('webcam-video', 'webcam-placeholder', 'start-webcam-btn', 'capture-photo-btn');
                }
            }
            if (id === 'edit-capture-photo-btn') {
                e.preventDefault();
                e.stopPropagation();
                capturePhoto('edit-webcam-video', 'edit-photo-canvas', 'edit-patient-photo-preview', 'edit-capture-photo-btn', 'edit-retake-photo-btn', 'edit-patientPhotoData');
            }
            if (id === 'edit-retake-photo-btn') {
                e.preventDefault();
                e.stopPropagation();
                const preview = document.getElementById('edit-patient-photo-preview');
                if (preview) preview.style.display = 'none';
                startWebcam('edit-webcam-video', 'edit-webcam-placeholder', 'edit-start-webcam-btn', 'edit-capture-photo-btn');
            }
        });
    }

    window.todayISO_BR = function() {
        // Retorna um objeto Date que representa "agora" no fuso de Brasília (UTC-3)
        // Independentemente de onde o servidor ou o navegador estejam
        const now = new Date();
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        const brOffset = -3;
        const brDate = new Date(utc + (3600000 * brOffset));
        console.log("DEBUG: Data Brasília calculada:", brDate.toDateString(), brDate.getHours() + ":" + brDate.getMinutes());
        return brDate;
    };

    window.selectToday = function() {
        selectedDate = todayISO_BR();
        console.log("Botão Hoje clicado. Nova data selecionada:", selectedDate.toISOString());
        const scheduleDate = document.getElementById('scheduleDate');
        if (scheduleDate) scheduleDate.textContent = formatDateBR(selectedDate);
        renderMiniCalendar();
        loadAppointments();
    };

    window.initializeDayView = function() {
        // Se a data já foi definida (ex: navegação), não reseta
        if (!selectedDate || isNaN(selectedDate.getTime())) {
            selectedDate = todayISO_BR();
        }
        console.log("Inicializando Agenda. Data Atual:", selectedDate.toISOString());
        const scheduleDate = document.getElementById('scheduleDate');
        if (scheduleDate) scheduleDate.textContent = formatDateBR(selectedDate);
        renderTimeColumn();
    };

    window.openNewAppointmentAtTime = function(hour, minutes) {
        const modalEl = document.getElementById('newAppointmentModal');
        if (!modalEl) {
            showAlert('Modal de agendamento nao encontrado', 'danger');
            return;
        }
        
        const dateField = document.getElementById('appointmentDate');
        const timeField = document.getElementById('appointmentTime');
        const doctorSelect = document.getElementById('appointmentDoctor');
        
        if (dateField) {
            const year = selectedDate.getFullYear();
            const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
            const day = String(selectedDate.getDate()).padStart(2, '0');
            dateField.value = `${year}-${month}-${day}`;
        }
        
        if (timeField) {
            timeField.value = `${String(hour).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
        }
        
        // Pre-selecionar medico do filtro atual (para secretaria)
        if (doctorSelect && currentDoctorFilter) {
            doctorSelect.value = currentDoctorFilter;
        }
        
        // Limpar campos do paciente
        const fieldsToReset = [
            'selectedPatientId', 'patientName', 'patientCode', 'patientCPF',
            'patientBirthDate', 'patientPhone', 'patientAddress', 'patientCity',
            'patientMotherName', 'patientIndicationSource', 'patientOccupation'
        ];
        fieldsToReset.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        
        new bootstrap.Modal(modalEl).show();
    };

    function renderTimeColumn() {
        const timeColumn = document.getElementById('timeColumn');
        if (!timeColumn) return;
        timeColumn.innerHTML = '';
        for (let hour = 7; hour <= 19; hour++) {
            for (let minutes = 0; minutes < 60; minutes += 15) {
                const slot = document.createElement('div');
                slot.className = 'hour-slot';
                slot.textContent = `${String(hour).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
                slot.style.cursor = 'pointer';
                slot.onclick = () => window.openNewAppointmentAtTime(hour, minutes);
                timeColumn.appendChild(slot);
            }
        }
    }

    window.renderMiniCalendar = function() {
        const miniCalendar = document.getElementById('miniCalendar');
        if (!miniCalendar) return;
        const today = new Date();
        const currentMonth = selectedDate.getMonth();
        const currentYear = selectedDate.getFullYear();
        const firstDay = new Date(currentYear, currentMonth, 1).getDay();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

        let html = `
            <div class="mini-calendar-header">
                <button onclick="previousMonth()"><i class="bi bi-chevron-left"></i></button>
                <div style="font-size: 14px; font-weight: 600;">
                    ${new Date(currentYear, currentMonth).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
                </div>
                <button onclick="nextMonth()"><i class="bi bi-chevron-right"></i></button>
            </div>
            <div class="mini-calendar-grid">
                ${['Dom','Seg','Ter','Qua','Qui','Sex','Sab'].map(d => `<div class="mini-calendar-day">${d}</div>`).join('')}
        `;
        for (let i = 0; i < firstDay; i++) html += '<div class="mini-calendar-date"></div>';
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(currentYear, currentMonth, day);
            const isSelected = date.toDateString() === selectedDate.toDateString();
            const isToday = date.toDateString() === today.toDateString();
            html += `<div class="mini-calendar-date ${isSelected ? 'selected' : ''} ${isToday ? 'today' : ''}" onclick="selectDate(new Date(${currentYear}, ${currentMonth}, ${day}))">${day}</div>`;
        }
        html += '</div>';
        miniCalendar.innerHTML = html;
    };

    function getAppointmentTypeClass(type) {
        const typeMap = {
            'Particular': 'appointment-particular',
            'Retorno': 'appointment-retorno',
            'UNIMED': 'appointment-unimed',
            'Cortesia': 'appointment-cortesia',
            'Transplante Capilar': 'appointment-transplante',
            'Cirurgia': 'appointment-cirurgia',
            'Botox': 'appointment-botox',
            'Laser': 'appointment-laser',
            'Preenchimento': 'appointment-preenchimento'
        };
        return typeMap[type] || 'appointment-particular';
    }

    function _buildAppointmentBlock(app) {
        const start = parseLocalDateTime(app.start);
        const timeStr = String(start.getHours()).padStart(2, '0') + ':' + String(start.getMinutes()).padStart(2, '0');
        const patientName = app.title ? app.title.split(' - ')[0] : 'Paciente';
        const ivpStars = app.extendedProps?.ivpStars;
        const starsHtml = ivpStars ? `<span class="text-warning ms-1">${'⭐'.repeat(ivpStars)}</span>` : '';

        const appointmentType = app.extendedProps?.appointmentType || app.appointmentType || 'Particular';
        const patientType = app.extendedProps?.patientType || app.patientType || 'Particular';
        const patientCode = app.extendedProps?.patientCode || null;
        const status = app.extendedProps?.status || app.status || 'agendado';
        const statusCadastral = app.extendedProps?.statusCadastral || 'ativo';
        const isProvisorio = statusCadastral === 'provisorio';
        const typeClass = getAppointmentTypeClass(appointmentType);
        const statusClass = `status-${status}`;
        const patientId = app.extendedProps?.patientId || app.patientId;
        const doctorId = app.extendedProps?.doctorId || app.doctorId;
        const isSurgeryMap = app.extendedProps?.isSurgeryMap || false;

        const block = document.createElement('div');
        block.className = `appointment-block ${typeClass} ${statusClass}${isProvisorio ? ' appointment-provisorio' : ''}`;
        if (isSurgeryMap) block.classList.add('appointment-cirurgia');
        block.style.cursor = 'pointer';
        block.dataset.appointmentId = app.id;

        const isWaiting = app.extendedProps?.waiting || app.waiting || false;
        let actionBadgeHtml = '';

        if (isProvisorio) {
            actionBadgeHtml = `<button class="btn btn-sm btn-warning btn-ativar-provisorio"
                    onclick="event.stopPropagation(); openEditAppointmentModalById('${app.id}')"
                    title="Editar cadastro provisório"><i class="bi bi-pencil-square"></i> Editar cadastro</button>`;
        } else if (status === 'atendido') {
            actionBadgeHtml = `<span class="atendido-badge"><i class="bi bi-check-circle-fill"></i> ATENDIDO</span>`;
        } else if (status === 'faltou') {
            actionBadgeHtml = `<span class="faltou-badge"><i class="bi bi-x-circle-fill"></i> FALTOU</span>
                    <button class="checkin-btn ms-2" onclick="event.stopPropagation(); doCheckin('${app.id}')" title="Chegou atrasado - Fazer Check-in"><i class="bi bi-box-arrow-in-right"></i> Check In</button>`;
        } else if (isWaiting) {
            actionBadgeHtml = `
                    <span class="waiting-badge"><i class="bi bi-hourglass-split"></i> Aguardando</span>
                    <button class="btn btn-sm btn-success ms-2" onclick="event.stopPropagation(); doCheckout('${app.id}')" title="Finalizar atendimento">
                        <i class="bi bi-check2-circle"></i> Finalizar
                    </button>
                    <button class="btn btn-sm btn-outline-danger ms-1" onclick="event.stopPropagation(); removeFromWaiting('${app.id}')" title="Remover da espera (sem finalizar)">
                        <i class="bi bi-x-circle"></i> Remover
                    </button>
                `;
        } else {
            actionBadgeHtml = `<button class="checkin-btn" onclick="event.stopPropagation(); doCheckin('${app.id}')" title="Fazer Check-in"><i class="bi bi-box-arrow-in-right"></i> Check In</button>`;
        }

        if (isProvisorio && (window.isSecretary || window.isDoctor)) {
            const existingPhone = app.extendedProps?.phone || '';
            actionBadgeHtml += `<button class="btn btn-sm btn-warning ms-1 btn-ativar-provisorio"
                    onclick="event.stopPropagation(); abrirModalAtivacao(${patientId}, '${patientName.replace(/'/g,"\\'")}', ${doctorId || 'null'}, '${(existingPhone || '').replace(/'/g,"\\'")}')"
                    title="Ativar cadastro deste paciente"><i class="bi bi-person-check"></i> Ativar</button>`;
        }

        if (isSurgeryMap && patientId) {
            actionBadgeHtml += `<button class="btn btn-sm btn-primary ms-2" onclick="event.stopPropagation(); goToPatientChart(${patientId}, '${app.id}')" title="Ver prontuário"><i class="bi bi-file-medical"></i> Prontuário</button>`;
        }

        const codeLabel = isProvisorio
            ? `<span class="badge bg-warning text-dark ms-1" style="font-size:0.65rem;vertical-align:middle;">⏳ PROVISÓRIO</span>`
            : `<span class="appointment-code">cod:${patientCode !== null ? patientCode : '-'}</span>`;

        block.innerHTML = `
                <div class="appointment-content">
                    <div class="appointment-info-line">
                        <span class="appointment-time-badge">${timeStr}</span>
                        <span class="appointment-name" onclick="event.stopPropagation(); if(${patientId || 0} && !${isProvisorio}) { goToPatientChart(${patientId || 0}, '${app.id}') } else if(${isProvisorio}) { showAlert('Cadastro provisório — ative primeiro para acessar o prontuário.', 'warning') } else { showAlert('Paciente não vinculado ao prontuário', 'warning') }" style="cursor:pointer; text-decoration:underline;">${patientName}${starsHtml}</span>
                        ${codeLabel}
                        <span class="appointment-type-label">pac:${patientType}</span>
                        <span class="appointment-consult-label">cons:${appointmentType}</span>
                        ${actionBadgeHtml}
                    </div>
                </div>
            `;

        block.onclick = () => selectAppointment(app);
        return block;
    }

    function updateProvisorioBadge() {
        const count = appointmentsList.filter(a => {
            const start = parseLocalDateTime(a.start);
            if (!start) return false;
            const appDateStr = start.getFullYear() + '-' +
                String(start.getMonth() + 1).padStart(2, '0') + '-' +
                String(start.getDate()).padStart(2, '0');
            const selDateStr = selectedDate.getFullYear() + '-' +
                String(selectedDate.getMonth() + 1).padStart(2, '0') + '-' +
                String(selectedDate.getDate()).padStart(2, '0');
            return appDateStr === selDateStr &&
                (a.extendedProps?.statusCadastral || 'ativo') === 'provisorio';
        }).length;
        const badge = document.getElementById('provisorioCounter');
        const countEl = document.getElementById('provisorioCount');
        if (badge && countEl) {
            countEl.textContent = count;
            badge.style.display = count > 0 ? '' : 'none';
        }
    }

    window.renderDayView = function() {
        const appointmentsGrid = document.getElementById('appointmentsGrid');
        if (!appointmentsGrid) return;
        appointmentsGrid.innerHTML = '';
        updateProvisorioBadge();

        console.log("Renderizando Agenda. Filtro Médico ID:", currentDoctorFilter);
        console.log("Total de agendamentos carregados:", appointmentsList.length);

        const dayAppointments = appointmentsList.filter(app => {
            const start = parseLocalDateTime(app.start);
            if (!start) return false;

            const appDateStr = start.getFullYear() + '-' +
                               String(start.getMonth() + 1).padStart(2, '0') + '-' +
                               String(start.getDate()).padStart(2, '0');

            const selectedDateStr = selectedDate.getFullYear() + '-' +
                                   String(selectedDate.getMonth() + 1).padStart(2, '0') + '-' +
                                   String(selectedDate.getDate()).padStart(2, '0');

            const isSameDate = appDateStr === selectedDateStr;

            const doctorId = parseInt(app.extendedProps?.doctorId || app.doctorId || app.doctor_id);
            const isDoctorMatch = !currentDoctorFilter || doctorId === currentDoctorFilter;

            return isSameDate && isDoctorMatch;
        });

        console.log("Agendamentos filtrados para exibição:", dayAppointments.length);

        if (dayAppointments.length === 0 && appointmentsList.length > 0) {
            console.log("DEBUG: Datas dos agendamentos carregados:", appointmentsList.map(a => a.start));
            console.log("DEBUG: Fuso horário local:", new Date().toString());
        }

        if (dayAppointments.length === 0) {
            appointmentsGrid.innerHTML = '<div class="empty-schedule">Nenhum agendamento para este dia</div>';
            return;
        }

        dayAppointments.sort((a, b) => parseLocalDateTime(a.start) - parseLocalDateTime(b.start));

        dayAppointments.forEach(app => {
            appointmentsGrid.appendChild(_buildAppointmentBlock(app));
        });
    };

    window.goToPatientChart = function(patientId, appointmentId, dpId) {
        if (dpId) {
            window.location.href = `/prontuario/dp/${dpId}`;
        } else if (patientId) {
            window.location.href = `/prontuario/${patientId}?appointment_id=${appointmentId}`;
        }
    };

    window.doCheckin = function(appointmentId) {
        fetch(`/espera/api/checkin/${appointmentId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showAlert('Check-in realizado!');
                loadAppointments();
                loadWaitingRoom();
            } else {
                showAlert(data.error || 'Erro no check-in', 'danger');
            }
        });
    };

    window.doCheckout = function(appointmentId) {
        fetch(`/espera/api/checkout/${appointmentId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() }
        })
        .then(r => r.json())
        .then(resp => {
            if (resp.success) {
                showAlert('Atendimento finalizado! Status: atendido');
                loadAppointments();
                loadWaitingRoom();
            } else {
                showAlert(resp.error || 'Erro ao finalizar atendimento', 'danger');
            }
        })
        .catch(err => {
            console.error(err);
            showAlert('Erro ao finalizar atendimento', 'danger');
        });
    };

    window.removeFromWaiting = function(appointmentId) {
        fetch(`/espera/api/remove/${appointmentId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() }
        })
        .then(r => r.json())
        .then(resp => {
            if (resp.success) {
                showAlert('Removido da espera (sem finalizar)');
                loadAppointments();
                loadWaitingRoom();
            } else {
                showAlert(resp.error || 'Erro ao remover da espera', 'danger');
            }
        })
        .catch(err => {
            console.error(err);
            showAlert('Erro ao remover da espera', 'danger');
        });
    };

    function _updateLastUpdatedLabel() {
        const el = document.getElementById('agendaLastUpdated');
        if (!el) return;
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        el.textContent = `Atualizado às ${h}:${m}`;
    }

    function _isAnyModalOpen() {
        return document.querySelector('.modal.show') !== null;
    }

    function _getAppointmentStateKey(app) {
        const status = app.extendedProps?.status || app.status || 'agendado';
        const waiting = !!(app.extendedProps?.waiting || app.waiting);
        const statusCadastral = app.extendedProps?.statusCadastral || 'ativo';
        return `${status}|${waiting}|${statusCadastral}`;
    }

    function _autoRefreshAppointments() {
        if (_isAnyModalOpen()) return;

        const year = selectedDate.getFullYear();
        const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(selectedDate.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
        let url = `/api/appointments?date=${dateStr}`;
        if (currentDoctorFilter) url += `&doctor_id=${currentDoctorFilter}`;

        fetch(url)
            .then(r => r.json())
            .then(newData => {
                if (_isAnyModalOpen()) return;

                const oldIds = new Set(appointmentsList.map(a => String(a.id)));
                const newIds = new Set(newData.map(a => String(a.id)));
                const sameIdSet = oldIds.size === newIds.size && [...newIds].every(id => oldIds.has(id));

                if (!sameIdSet) {
                    appointmentsList = newData;
                    renderDayView();
                    _updateLastUpdatedLabel();
                    if (calendar && currentView === 'month') calendar.refetchEvents();
                    return;
                }

                const oldMap = {};
                appointmentsList.forEach(a => { oldMap[String(a.id)] = a; });

                let anyChanged = false;
                newData.forEach(newApp => {
                    const oldApp = oldMap[String(newApp.id)];
                    if (!oldApp) return;
                    if (_getAppointmentStateKey(newApp) !== _getAppointmentStateKey(oldApp)) {
                        const existing = document.querySelector(`[data-appointment-id="${newApp.id}"]`);
                        if (existing) {
                            existing.parentNode.replaceChild(_buildAppointmentBlock(newApp), existing);
                        }
                        anyChanged = true;
                    }
                });

                appointmentsList = newData;
                _updateLastUpdatedLabel();
                if (anyChanged) updateProvisorioBadge();
                if (anyChanged && calendar && currentView === 'month') calendar.refetchEvents();
            })
            .catch(err => console.error('Erro no auto-refresh da agenda:', err));
    }

    window.loadAppointments = function() {
        const year = selectedDate.getFullYear();
        const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(selectedDate.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
        
        let url = `/api/appointments?date=${dateStr}`;
        if (currentDoctorFilter) url += `&doctor_id=${currentDoctorFilter}`;

        console.log("Carregando agendamentos. URL:", url, "Data Selecionada:", dateStr);

        fetch(url)
            .then(r => r.json())
            .then(data => {
                appointmentsList = data;
                console.log("Agendamentos recebidos do servidor:", appointmentsList.length);
                renderDayView();
                _updateLastUpdatedLabel();
                if (calendar && currentView === 'month') calendar.refetchEvents();
            })
            .catch(err => {
                console.error('Erro ao carregar agendamentos:', err);
            });
    };

    window.selectDate = function(date) {
        selectedDate = new Date(date);
        console.log("Data selecionada:", selectedDate.toDateString());
        const scheduleDate = document.getElementById('scheduleDate');
        if (scheduleDate) scheduleDate.textContent = formatDateBR(selectedDate);
        renderMiniCalendar();
        loadAppointments();
    };

    window.previousMonth = function() { selectedDate.setMonth(selectedDate.getMonth() - 1); renderMiniCalendar(); };
    window.nextMonth = function() { selectedDate.setMonth(selectedDate.getMonth() + 1); renderMiniCalendar(); };
    window.previousDay = function() { 
        selectedDate.setDate(selectedDate.getDate() - 1); 
        window.selectDate(selectedDate); 
    };
    window.nextDay = function() { 
        selectedDate.setDate(selectedDate.getDate() + 1); 
        window.selectDate(selectedDate); 
    };
    window.todayDay = function() { 
        window.selectToday();
    };

    function selectAppointment(app) {
        currentEvent = app;
        if (window.isSecretary) {
            openEditAppointmentModal(app);
        } else {
            showEventDetails(app);
        }
    }

    function openEditAppointmentModal(app) {
        const modalEl = document.getElementById('editAppointmentModal');
        if (!modalEl) {
            showEventDetails(app);
            return;
        }
        document.getElementById('editAppointmentId').value = app.id;
        const props = app.extendedProps || {};
        const isProvisorio = (props.statusCadastral || 'ativo') === 'provisorio';
        document.getElementById('editPatientName').value = app.title.split(' - ')[0];
        document.getElementById('editPatientName').readOnly = !isProvisorio;
        document.getElementById('editPatientPhone').value = props.phone || '';
        document.getElementById('editPatientPhone').readOnly = !isProvisorio;
        const extraFields = {
            editPatientCPF: props.cpf || '',
            editPatientBirthDate: props.birthDate || '',
            editPatientAddress: props.address || '',
            editPatientCity: props.city || '',
            editPatientMotherName: props.motherName || '',
            editPatientIndicationSource: props.indicationSource || '',
            editPatientOccupation: props.occupation || ''
        };
        Object.entries(extraFields).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) el.value = value;
        });
        document.querySelectorAll('#editAppointmentModal .provisional-edit-only').forEach(el => {
            el.style.display = isProvisorio ? '' : 'none';
        });
        const editStatusNote = document.getElementById('editProvisionalStatusNote');
        if (editStatusNote) editStatusNote.remove();
        if (isProvisorio) {
            const note = document.createElement('div');
            note.id = 'editProvisionalStatusNote';
            note.className = 'alert alert-warning py-2';
            note.innerHTML = '<strong>Cadastro provisório:</strong> edite os dados antes de ativar. Check-in fica indisponível até a ativação.';
            modalEl.querySelector('.modal-body').prepend(note);
        }
        const start = parseLocalDateTime(app.start);
        document.getElementById('editAppointmentDate').value = start.toISOString().split('T')[0];
        document.getElementById('editAppointmentTime').value = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`;
        document.getElementById('editPatientType').value = props.patientType || 'Particular';
        document.getElementById('editAppointmentType').value = props.appointmentType || 'Particular';
        const durationMinutes = app.end ? Math.max(15, Math.round((parseLocalDateTime(app.end) - start) / 60000)) : 15;
        document.getElementById('editAppointmentDuration').value = durationMinutes;
        const notesEl = document.getElementById('editAppointmentNotes');
        if (notesEl) notesEl.value = props.notes || '';
        
        // Adicionar botão de deletar se não existir
        let footer = modalEl.querySelector('.modal-footer');
        if (footer && !document.getElementById('btnDeleteAppointment')) {
            const btnDelete = document.createElement('button');
            btnDelete.id = 'btnDeleteAppointment';
            btnDelete.className = 'btn btn-danger me-auto';
            btnDelete.innerHTML = '<i class="bi bi-trash"></i> Excluir';
            btnDelete.onclick = () => window.deleteAppointment(app.id);
            footer.prepend(btnDelete);
        } else if (document.getElementById('btnDeleteAppointment')) {
            document.getElementById('btnDeleteAppointment').onclick = () => window.deleteAppointment(app.id);
        }
        
        new bootstrap.Modal(modalEl).show();
    }

    window.openEditAppointmentModalById = function(appointmentId) {
        const app = appointmentsList.find(a => String(a.id) === String(appointmentId));
        if (app) openEditAppointmentModal(app);
    };

    window.deleteAppointment = function(id) {
        if (!confirm('Deseja realmente excluir este agendamento?')) return;
        
        fetch(`/api/appointments/${id}`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showAlert('Agendamento excluido!');
                const modalEl = document.getElementById('editAppointmentModal');
                if (modalEl) {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }
                loadAppointments();
            } else {
                showAlert(data.error || 'Erro ao excluir', 'danger');
            }
        });
    };

    window.searchPatientsDetailed = function() {
        const q = document.getElementById('patientSearchInput').value.trim();
        if (q.length < 2) return;
        const body = document.getElementById('patientSearchResults');
        body.innerHTML = '<tr><td colspan="4">Buscando...</td></tr>';

        const params = new URLSearchParams({ q });
        if (currentDoctorFilter) {
            params.set('doctor_id', String(currentDoctorFilter));
        }

        fetch(`/api/doctor-patients/search?${params.toString()}`)
            .then(r => r.json())
            .then(data => {
                body.innerHTML = data.length ? data.map(p => `
                    <tr>
                        <td>${p.patient_name}</td>
                        <td>${p.patient_code ?? '-'}</td>
                        <td>Dr(a). ${p.doctor_name} (${p.doctor_role || 'DERM'})</td>
                        <td><button class="btn btn-sm btn-primary" onclick="goToPatientChart(${p.patient_id}, null, ${p.dp_id})">Prontuário</button></td>
                    </tr>`).join('') : '<tr><td colspan="4">Nenhum encontrado</td></tr>';
            });
    };

    window.openPatientDetail = function(id) {
        fetch(`/api/patient/${id}/history`)
            .then(r => r.json())
            .then(data => {
                const p = data.patient;
                document.getElementById('detailPatientId').value = p.id;
                document.getElementById('detailPatientName').value = p.name;
                const list = document.getElementById('patientHistoryList');
                list.innerHTML = data.history.map(h => `<div class="card mb-2 p-2 small"><b>${h.date}</b><br>${h.content}</div>`).join('');
                const searchModal = bootstrap.Modal.getInstance(document.getElementById('searchPatientModal'));
                if (searchModal) searchModal.hide();
                new bootstrap.Modal(document.getElementById('patientDetailModal')).show();
            });
    };

    window.savePatientChanges = function() {
        const id = document.getElementById('detailPatientId').value;
        const data = { name: document.getElementById('detailPatientName').value };
        fetch(`/api/patients/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify(data)
        }).then(r => r.json()).then(res => showAlert(res.success ? 'Salvo!' : 'Erro'));
    };

    window.initializeMonthCalendar = function() {
        const el = document.getElementById('calendar');
        if (!el || typeof FullCalendar === 'undefined') return;
        calendar = new FullCalendar.Calendar(el, {
            locale: 'pt-br',
            initialView: 'dayGridMonth',
            events: '/api/appointments',
            eventClick: (info) => { currentEvent = info.event; showEventDetails(info.event); }
        });
        calendar.render();
    };

    window.updateWaitingCounter = function() {
        fetch('/espera/api/stats').then(r => r.json()).then(s => {
            const el = document.getElementById('waitingCount');
            if (el) el.textContent = s.count || 0;
        });
    };

    window.startWaitingRoomUpdates = function() {
        loadWaitingRoom();
        setInterval(loadWaitingRoom, 30000);
    };

    function minutesSince(iso) {
        if (!iso) return 0;
        const t = new Date(iso).getTime();
        if (isNaN(t)) return 0;
        return Math.max(0, Math.floor((Date.now() - t) / 60000));
    }

    window.startWaitingClock = function() {
        setInterval(function() {
            document.querySelectorAll('#waitingRoomList .waiting-patient-item').forEach(function(el) {
                const iso = el.getAttribute('data-checkedin');
                const span = el.querySelector('[data-role="wait"]');
                if (span && iso) {
                    span.textContent = minutesSince(iso) + ' min';
                }
            });
        }, 1000);
    };

    function loadWaitingRoom() {
        fetch('/espera/api/list').then(r => r.json()).then(d => {
            const list = document.getElementById('waitingRoomList');
            if (!list) return;
            const items = d.waiting_list || [];
            waitingRoomData = items;
            list.innerHTML = items.length ? items.map(p => `
                <div class="waiting-patient-item" data-checkedin="${p.checked_in_time || ''}" onclick="goToPatientChart(${p.patient_id}, ${p.appointment_id})" style="cursor:pointer; padding: 8px; border-bottom: 1px solid #eee; transition: background 0.2s;">
                    <div class="d-flex justify-content-between align-items-center">
                        <span style="font-weight: 500;">${p.patient_name}</span>
                        <small class="text-muted">(<span data-role="wait">${(p.wait_time_minutes ?? 0)} min</span>)</small>
                    </div>
                </div>`).join('') : '<div class="waiting-empty">Sala de espera vazia</div>';
            
            // Adicionar hover effect via JS se necessário, mas CSS é melhor
        });
    }


    // Garantir que o botão de salvar chama a função correta
    document.addEventListener('DOMContentLoaded', function() {
        const saveBtn = document.querySelector('#appointmentForm button[type="submit"]') || 
                        document.querySelector('#newAppointmentModal .btn-primary:last-child');
        if (saveBtn) {
            saveBtn.onclick = (e) => {
                e.preventDefault();
                window.saveAppointment();
            };
        }
    });

    function formatDateBR(date) {
        const days = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];
        const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        return `${days[date.getDay()]}, ${date.getDate()} de ${months[date.getMonth()]} de ${date.getFullYear()}`;
    }

    window.showEventDetails = function(event) {
        let props, patientName, startDate, endDate;
        
        if (event.extendedProps) {
            props = event.extendedProps;
            patientName = event.title ? event.title.split(' - ')[0] : 'Paciente';
            startDate = typeof event.start === 'string' ? parseLocalDateTime(event.start) : event.start;
            endDate = typeof event.end === 'string' ? parseLocalDateTime(event.end) : event.end;
        } else {
            props = event;
            patientName = event.title ? event.title.split(' - ')[0] : 'Paciente';
            startDate = parseLocalDateTime(event.start);
            endDate = parseLocalDateTime(event.end);
        }
        
        if (!startDate) startDate = new Date();
        if (!endDate) endDate = new Date(startDate.getTime() + 30*60*1000);
        
        function formatToLocalDateTime(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}`;
        }
        
        const startDateTime = formatToLocalDateTime(startDate);
        const endDateTime = formatToLocalDateTime(endDate);
        
        const statusLabels = {
            'agendado': 'Agendado',
            'confirmado': 'Confirmado',
            'atendido': 'Atendido',
            'faltou': 'Faltou'
        };
        
        const appointmentTypes = ['Particular', 'Botox', 'Retorno Botox', 'Laser', 'Preenchimento', 'Ulthera', 'Infiltração Capilar', 'Soroterapia', 'Pequena Cirurgia', 'Retirada de Ponto', 'Nitrogênio Líquido', 'Transplante Capilar', 'Retorno', 'UNIMED', 'Cortesia'];
        const isSecretary = window.isSecretary === true;
        
        let detailsHtml = '';
        
        if (isSecretary) {
            detailsHtml = `
                <div class="mb-3">
                    <label class="form-label"><strong>Paciente</strong></label>
                    <input type="text" class="form-control" id="modalEditPatientName" value="${patientName}">
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Data/Hora Início</strong></label>
                    <input type="datetime-local" class="form-control" id="modalEditStartTime" value="${startDateTime}">
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Data/Hora Fim</strong></label>
                    <input type="datetime-local" class="form-control" id="modalEditEndTime" value="${endDateTime}">
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Telefone</strong></label>
                    <input type="tel" class="form-control" id="modalEditPhone" value="${props.phone || ''}">
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Tipo de Consulta</strong></label>
                    <select class="form-select" id="modalEditAppointmentType">
                        ${appointmentTypes.map(type => `<option value="${type}" ${props.appointmentType === type ? 'selected' : ''}>${type}</option>`).join('')}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Status</strong></label>
                    <select class="form-select" id="modalEditStatus">
                        <option value="agendado" ${props.status === 'agendado' ? 'selected' : ''}>Agendado</option>
                        <option value="confirmado" ${props.status === 'confirmado' ? 'selected' : ''}>Confirmado</option>
                        <option value="atendido" ${props.status === 'atendido' ? 'selected' : ''}>Atendido</option>
                        <option value="faltou" ${props.status === 'faltou' ? 'selected' : ''}>Faltou</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Observações</strong></label>
                    <textarea class="form-control" id="modalEditNotes" rows="3">${props.notes || ''}</textarea>
                </div>
            `;
        } else {
            const appointmentType = props.appointmentType || 'Particular';
            const status = props.status || 'agendado';
            const patientId = props.patientId;
            detailsHtml = `
                <p><strong>Paciente:</strong> <a href="#" onclick="goToPatientChart(${patientId}, ${currentEvent?.id || event.id}); return false;">${patientName}</a></p>
                <p><strong>Data/Hora:</strong> ${startDate.toLocaleDateString('pt-BR')} ${String(startDate.getHours()).padStart(2,'0')}:${String(startDate.getMinutes()).padStart(2,'0')}</p>
                <p><strong>Tipo:</strong> ${appointmentType}</p>
                <p><strong>Status:</strong> <span class="badge bg-secondary">${statusLabels[status]}</span></p>
                ${props.phone ? `<p><strong>Telefone:</strong> ${props.phone}</p>` : ''}
                ${props.notes ? `<p><strong>Observações:</strong> ${props.notes}</p>` : ''}
                <div class="mt-3">
                    <label class="form-label">Alterar Status:</label>
                    <select class="form-select" id="eventStatusUpdate">
                        <option value="agendado" ${status === 'agendado' ? 'selected' : ''}>Agendado</option>
                        <option value="confirmado" ${status === 'confirmado' ? 'selected' : ''}>Confirmado</option>
                        <option value="atendido" ${status === 'atendido' ? 'selected' : ''}>Atendido</option>
                        <option value="faltou" ${status === 'faltou' ? 'selected' : ''}>Faltou</option>
                    </select>
                    <button class="btn btn-sm btn-primary mt-2" onclick="updateEventStatus()">Atualizar Status</button>
                </div>
            `;
        }
        
        const detailsEl = document.getElementById('eventDetails');
        if (detailsEl) detailsEl.innerHTML = detailsHtml;
        
        const footer = document.querySelector('#eventDetailModal .modal-footer');
        if (footer) {
            let saveBtn = document.getElementById('saveEditBtn');
            if (isSecretary) {
                if (!saveBtn) {
                    saveBtn = document.createElement('button');
                    saveBtn.id = 'saveEditBtn';
                    saveBtn.type = 'button';
                    saveBtn.className = 'btn btn-success';
                    saveBtn.innerHTML = '<i class="bi bi-save"></i> Salvar Alterações';
                    saveBtn.onclick = window.saveAppointmentEdits;
                    footer.insertBefore(saveBtn, footer.firstChild);
                }
            } else {
                if (saveBtn) saveBtn.remove();
            }
        }
        
        const modalEl = document.getElementById('eventDetailModal');
        if (modalEl) new bootstrap.Modal(modalEl).show();
    };

    window.saveAppointmentEdits = function() {
        const startStr = document.getElementById('modalEditStartTime').value;
        const endStr = document.getElementById('modalEditEndTime').value;
        const payload = {
            patientName: document.getElementById('modalEditPatientName').value,
            start: startStr + ':00',
            end: endStr + ':00',
            phone: document.getElementById('modalEditPhone').value,
            appointmentType: document.getElementById('modalEditAppointmentType').value,
            status: document.getElementById('modalEditStatus').value,
            notes: document.getElementById('modalEditNotes').value
        };
        fetch(`/api/appointments/${currentEvent.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify(payload)
        }).then(r => r.json()).then(data => {
            if (data.success) {
                showAlert('Atualizado!');
                loadAppointments();
                const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailModal'));
                if (modal) modal.hide();
            } else {
                showAlert(data.error || 'Erro', 'danger');
            }
        });
    };

    window.updateEventStatus = function() {
        const newStatus = document.getElementById('eventStatusUpdate').value;
        fetch(`/api/appointments/${currentEvent.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ status: newStatus })
        }).then(r => r.json()).then(data => {
            if (data.success) {
                showAlert('Status atualizado!');
                loadAppointments();
                const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailModal'));
                if (modal) modal.hide();
            }
        });
    };

    window.openPatientChart = function() {
        let patientId = currentEvent?.extendedProps?.patientId || currentEvent?.patientId;
        if (patientId) {
            window.location.href = `/prontuario/${patientId}?appointment_id=${currentEvent.id}`;
        }
    };

    window.filterByDoctor = function(doctorId, btn) {
        currentDoctorFilter = doctorId === 'all' ? null : parseInt(doctorId);
        
        // Armazenar preferência de filtro no localStorage para não perder ao navegar
        if (currentDoctorFilter) {
            localStorage.setItem('agenda_doctor_filter', currentDoctorFilter);
        } else {
            localStorage.removeItem('agenda_doctor_filter');
        }

        loadAppointments();
        if (calendar) calendar.refetchEvents();
        
        // Atualizar botoes de filtro
        document.querySelectorAll('.doctor-filter-btns .btn').forEach(b => {
            b.classList.remove('active');
        });
        if (btn) {
            btn.classList.add('active');
        } else {
            // Se nao passou o botao, tenta achar pelo doctorId
            const targetBtn = document.querySelector(`.doctor-filter-btns button[onclick*="'${doctorId}'"]`) || 
                             document.querySelector(`.doctor-filter-btns button[onclick*="${doctorId}"]`);
            if (targetBtn) targetBtn.classList.add('active');
        }
        
        // Pre-selecionar medico no formulario de novo agendamento
        const doctorSelect = document.getElementById('appointmentDoctor');
        if (doctorSelect && currentDoctorFilter) {
            doctorSelect.value = currentDoctorFilter;
        }
    };

    window.switchView = function(view) {
        currentView = view;
        const dayContent = document.getElementById('dayViewContent');
        const monthContent = document.getElementById('monthViewContent');
        const dayBtn = document.getElementById('dayViewBtn');
        const monthBtn = document.getElementById('monthViewBtn');
        
        if (view === 'day') {
            if (dayContent) dayContent.style.display = 'grid';
            if (monthContent) monthContent.style.display = 'none';
            if (dayBtn) dayBtn.classList.add('active');
            if (monthBtn) monthBtn.classList.remove('active');
        } else {
            if (dayContent) dayContent.style.display = 'none';
            if (monthContent) monthContent.style.display = 'block';
            if (dayBtn) dayBtn.classList.remove('active');
            if (monthBtn) monthBtn.classList.add('active');
            if (!calendar) initializeMonthCalendar();
        }
    };

    window.showDuplicatePatientModal = function(data) {
        const listEl = document.getElementById('duplicatePatientList');
        const msgEl = document.getElementById('duplicatePatientMessage');
        if (!listEl) return;
        if (msgEl && data.message) msgEl.textContent = data.message;

        const dups = data.duplicates || [];
        listEl.innerHTML = dups.map(d => {
            const codeBadge = d.patient_code
                ? `<span class="badge bg-primary ms-2">Cód. ${d.patient_code}</span>`
                : '<span class="badge bg-secondary ms-2">Sem código</span>';
            const phone = d.phone ? ` · ${d.phone}` : '';
            const city = d.city ? ` · ${d.city}` : '';
            return `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${d.name}</strong>${codeBadge}
                        <div class="text-muted small">${(d.cpf || 'Sem CPF')}${phone}${city}</div>
                    </div>
                    <button type="button" class="btn btn-sm btn-success" onclick="openExistingPatient(${d.id})">
                        <i class="bi bi-folder2-open"></i> Abrir ficha
                    </button>
                </div>`;
        }).join('');

        const modalEl = document.getElementById('duplicatePatientModal');
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    };

    window.openExistingPatient = function(patientId) {
        const modalEl = document.getElementById('duplicatePatientModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        if (typeof goToPatientChart === 'function') {
            goToPatientChart(patientId, null);
        } else {
            window.location.href = `/prontuario/${patientId}`;
        }
    };

    (function() {
        const btn = document.getElementById('duplicateCreateAnywayBtn');
        if (btn) {
            btn.addEventListener('click', function() {
                const modalEl = document.getElementById('duplicatePatientModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
                window._forceCreatePatient = true;
                window.saveAppointment();
            });
        }
    })();

    window.saveAppointment = function() {
        const saveBtn = document.querySelector('#appointmentForm button[type="submit"]') || 
                        document.querySelector('#newAppointmentModal .btn-primary:last-child');
        
        if (saveBtn && saveBtn.disabled) return;
        if (saveBtn) {
            saveBtn.disabled = true;
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
        }

        const patientId = document.getElementById('selectedPatientId')?.value || '';
        const patientName = document.getElementById('patientName')?.value || '';
        const patientCode = document.getElementById('patientCode')?.value || '';
        const patientCPF = document.getElementById('patientCPF')?.value || '';
        const patientBirthDate = document.getElementById('patientBirthDate')?.value || '';
        const patientPhone = document.getElementById('patientPhone')?.value || '';
        const patientAddress = document.getElementById('patientAddress')?.value || '';
        const patientCity = document.getElementById('patientCity')?.value || '';
        const patientMotherName = document.getElementById('patientMotherName')?.value || '';
        const patientIndicationSource = document.getElementById('patientIndicationSource')?.value || '';
        const patientOccupation = document.getElementById('patientOccupation')?.value || '';
        const patientType = document.getElementById('patientType')?.value || 'Particular';
        const appointmentType = document.getElementById('appointmentType')?.value || 'Particular';
        const appointmentDate = document.getElementById('appointmentDate')?.value || '';
        const appointmentTime = document.getElementById('appointmentTime')?.value || '';
        const appointmentDuration = document.getElementById('appointmentDuration')?.value || 15;
        const appointmentDoctor = document.getElementById('appointmentDoctor')?.value || '';
        const photoData = document.getElementById('patientPhotoData')?.value || '';

        if (!patientName) {
            showAlert('Nome do paciente é obrigatório', 'danger');
            return;
        }
        if (!appointmentDate || !appointmentTime) {
            showAlert('Data e hora são obrigatórias', 'danger');
            return;
        }

        const payload = {
            patient_id: patientId && patientId !== "" ? parseInt(patientId) : null,
            patientName: patientName,
            patient_code: patientCode,
            cpf: patientCPF,
            birth_date: patientBirthDate,
            phone: patientPhone,
            address: patientAddress,
            city: patientCity,
            mother_name: patientMotherName,
            indication_source: patientIndicationSource,
            occupation: patientOccupation,
            patientType: patientType,
            appointmentType: appointmentType,
            start: `${appointmentDate}T${appointmentTime}:00`,
            end: (function() {
                const parts = appointmentDate.split('-');
                const timeParts = appointmentTime.split(':');
                const startDate = new Date(parts[0], parts[1]-1, parts[2], timeParts[0], timeParts[1]);
                const endDate = new Date(startDate.getTime() + parseInt(appointmentDuration) * 60000);
                const ey = endDate.getFullYear();
                const em = String(endDate.getMonth() + 1).padStart(2, '0');
                const ed = String(endDate.getDate()).padStart(2, '0');
                const eh = String(endDate.getHours()).padStart(2, '0');
                const emin = String(endDate.getMinutes()).padStart(2, '0');
                return `${ey}-${em}-${ed}T${eh}:${emin}:00`;
            })(),
            doctor_id: appointmentDoctor || null,
            photo_data: photoData
        };

        if (window._forceCreatePatient) {
            payload.force_create = true;
            window._forceCreatePatient = false;
        }

        fetch('/api/appointments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(data => {
            if (data.warning === 'duplicate_found') {
                showDuplicatePatientModal(data);
                return;
            }
            if (data.success) {
                showAlert('Agendamento salvo com sucesso!');
                loadAppointments();
                const modal = bootstrap.Modal.getInstance(document.getElementById('newAppointmentModal'));
                if (modal) modal.hide();
                
                // Limpar formulário
                const form = document.getElementById('appointmentForm');
                if (form) form.reset();
                
                const idsToClear = ['selectedPatientId', 'patientPhotoData', 'patientCode', 'patientCPF', 'patientBirthDate', 'patientPhone', 'patientAddress', 'patientCity', 'patientMotherName', 'patientIndicationSource', 'patientOccupation'];
                idsToClear.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.value = '';
                });

                // Reset webcam UI
                const preview = document.getElementById('patient-photo-preview');
                if (preview) preview.style.display = 'none';
                const placeholder = document.getElementById('webcam-placeholder');
                if (placeholder) placeholder.style.display = 'flex';
                const video = document.getElementById('webcam-video');
                if (video) video.style.display = 'none';
                const startBtn = document.getElementById('start-webcam-btn');
                if (startBtn) startBtn.style.display = 'inline-block';
            } else {
                showAlert(data.error || 'Erro ao salvar', 'danger');
            }
        })
        .catch(err => {
            console.error('Erro:', err);
            showAlert('Erro ao salvar agendamento', 'danger');
        })
        .finally(() => {
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = 'Salvar Agendamento';
            }
        });
    };

    window.deleteAppointment = function() {
        if (!currentEvent) {
            showAlert('Nenhum agendamento selecionado', 'danger');
            return;
        }
        if (!confirm('Tem certeza que deseja excluir este agendamento?')) {
            return;
        }
        fetch(`/api/appointments/${currentEvent.id}`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showAlert('Agendamento excluído!');
                loadAppointments();
                const modal = bootstrap.Modal.getInstance(document.getElementById('editAppointmentModal'));
                if (modal) modal.hide();
            } else {
                showAlert(data.error || 'Erro ao excluir', 'danger');
            }
        });
    };

    window.updateAppointmentFromEdit = function() {
        const appointmentId = document.getElementById('editAppointmentId')?.value;
        if (!appointmentId) {
            showAlert('Agendamento não encontrado', 'danger');
            return;
        }

        const patientName = document.getElementById('editPatientName')?.value || '';
        const patientPhone = document.getElementById('editPatientPhone')?.value || '';
        const patientCPF = document.getElementById('editPatientCPF')?.value || '';
        const patientBirthDate = document.getElementById('editPatientBirthDate')?.value || '';
        const patientAddress = document.getElementById('editPatientAddress')?.value || '';
        const patientCity = document.getElementById('editPatientCity')?.value || '';
        const patientMotherName = document.getElementById('editPatientMotherName')?.value || '';
        const patientIndicationSource = document.getElementById('editPatientIndicationSource')?.value || '';
        const patientOccupation = document.getElementById('editPatientOccupation')?.value || '';
        const patientType = document.getElementById('editPatientType')?.value || 'Particular';
        const appointmentType = document.getElementById('editAppointmentType')?.value || 'Particular';
        const appointmentNotes = document.getElementById('editAppointmentNotes')?.value || '';
        const appointmentDate = document.getElementById('editAppointmentDate')?.value || '';
        const appointmentTime = document.getElementById('editAppointmentTime')?.value || '';
        const appointmentDuration = parseInt(document.getElementById('editAppointmentDuration')?.value || 15);
        const photoData = document.getElementById('edit-patientPhotoData')?.value || '';

        let startDateTime = null;
        let endDateTime = null;
        if (appointmentDate && appointmentTime) {
            startDateTime = `${appointmentDate}T${appointmentTime}:00`;
            const startDate = new Date(`${appointmentDate}T${appointmentTime}`);
            const endDate = new Date(startDate.getTime() + appointmentDuration * 60000);
            const endTimeStr = `${String(endDate.getHours()).padStart(2, '0')}:${String(endDate.getMinutes()).padStart(2, '0')}:00`;
            endDateTime = `${appointmentDate}T${endTimeStr}`;
        }

        const payload = {
            patientName: patientName,
            phone: patientPhone,
            cpf: patientCPF,
            birth_date: patientBirthDate,
            address: patientAddress,
            city: patientCity,
            mother_name: patientMotherName,
            indication_source: patientIndicationSource,
            occupation: patientOccupation,
            patientType: patientType,
            appointmentType: appointmentType,
            notes: appointmentNotes,
            photo_data: photoData
        };
        if (startDateTime) payload.start = startDateTime;
        if (endDateTime) payload.end = endDateTime;

        fetch(`/api/appointments/${appointmentId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showAlert('Agendamento atualizado!');
                loadAppointments();
                const modal = bootstrap.Modal.getInstance(document.getElementById('editAppointmentModal'));
                if (modal) modal.hide();
            } else {
                showAlert(data.error || 'Erro ao atualizar', 'danger');
            }
        });
    };

    window.deleteEvent = function() {
        if (!currentEvent) {
            showAlert('Nenhum evento selecionado', 'danger');
            return;
        }
        if (!confirm('Tem certeza que deseja excluir este agendamento?')) {
            return;
        }
        fetch(`/api/appointments/${currentEvent.id}`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showAlert('Agendamento excluído!');
                loadAppointments();
                const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailModal'));
                if (modal) modal.hide();
            } else {
                showAlert(data.error || 'Erro ao excluir', 'danger');
            }
        });
    };

    // Webcam functionality
    let stream = null;
    const video = document.getElementById('webcam-video');
    const canvas = document.getElementById('photo-canvas');
    const preview = document.getElementById('patient-photo-preview');
    const placeholder = document.getElementById('webcam-placeholder');
    const startBtn = document.getElementById('start-webcam-btn');
    const captureBtn = document.getElementById('capture-photo-btn');
    const retakeBtn = document.getElementById('retake-photo-btn');
    const photoDataInput = document.getElementById('patientPhotoData');

    if (startBtn) {
        startBtn.onclick = async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 }, audio: false });
                video.srcObject = stream;
                video.style.display = 'block';
                placeholder.style.display = 'none';
                preview.style.display = 'none';
                startBtn.style.display = 'none';
                captureBtn.style.display = 'inline-block';
            } catch (err) {
                console.error("Erro ao acessar webcam:", err);
                showAlert("Não foi possível acessar a câmera. Verifique as permissões.", "danger");
            }
        };
    }

    if (captureBtn) {
        captureBtn.onclick = () => {
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const dataURL = canvas.toDataURL('image/jpeg', 0.8);
            photoDataInput.value = dataURL;
            
            preview.src = dataURL;
            preview.style.display = 'block';
            video.style.display = 'none';
            captureBtn.style.display = 'none';
            retakeBtn.style.display = 'inline-block';
            
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }

    if (retakeBtn) {
        retakeBtn.onclick = () => {
            photoDataInput.value = '';
            preview.style.display = 'none';
            retakeBtn.style.display = 'none';
            startBtn.click();
        };
    }

})();

// ── Ativação de cadastro provisório ──────────────────────────────────────────
window._ativarCtx = { patientId: null, doctorId: null, warnings: [] };

function renderActivationWarnings(data, patientId, doctorId) {
    window._ativarCtx.warnings = data.warnings || [];
    const alertaDiv = document.getElementById('ativarAlertas');
    const lista = document.getElementById('ativarAlertalista');
    alertaDiv.classList.remove('d-none');

    const mergeDiv = document.getElementById('ativarMergeOpcoes');
    const mergeLista = document.getElementById('ativarMergeLista');
    mergeDiv.classList.remove('d-none');

    lista.innerHTML = '';
    mergeLista.innerHTML = '';
    data.warnings.forEach(w => {
        const reasonLabel = {
            'nome_semelhante': 'Nome semelhante',
            'mesmo_cpf': 'Mesmo CPF',
            'mesmo_telefone': 'Mesmo telefone'
        }[w.reason] || w.reason;

        lista.innerHTML += `<div class="small mb-1">
            <span class="badge bg-secondary">${reasonLabel}</span>
            <strong>${w.name}</strong>
            ${w.phone ? `· ${w.phone}` : ''}
            ${w.cpf ? `· CPF: ${w.cpf}` : ''}
        </div>`;

        mergeLista.innerHTML += `<button class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2"
            onclick="event.stopPropagation(); const phone = document.getElementById('ativarTelefonePaciente').value.trim(); if(!phone){document.getElementById('ativarTelefoneErro').classList.remove('d-none');return;}document.getElementById('ativarTelefoneErro').classList.add('d-none');_finalizarAtivacao(${patientId}, ${doctorId}, ${w.id}, true, phone)">
            <span><strong>${w.name}</strong>
            ${w.phone ? `<span class='text-muted ms-2 small'>${w.phone}</span>` : ''}
            ${w.cpf ? `<span class='text-muted ms-2 small'>CPF: ${w.cpf}</span>` : ''}
            <span class='ms-2 badge bg-secondary small'>${reasonLabel}</span></span>
            <span class="badge bg-primary">Vincular</span>
        </button>`;
    });

    document.getElementById('ativarInstrucao').textContent =
        'Foram encontrados cadastros possivelmente duplicados. Escolha vincular a um existente ou ativar como novo.';
}

window.abrirModalAtivacao = function(patientId, patientName, doctorId, existingPhone) {
    window._ativarCtx = { patientId, doctorId, warnings: [] };

    document.getElementById('ativarNomePaciente').textContent = patientName;
    const telInput = document.getElementById('ativarTelefonePaciente');
    telInput.value = existingPhone || '';
    document.getElementById('ativarTelefoneErro').classList.add('d-none');
    document.getElementById('ativarAlertas').classList.add('d-none');
    document.getElementById('ativarAlertalista').innerHTML = '';
    document.getElementById('ativarMergeOpcoes').classList.add('d-none');
    document.getElementById('ativarMergeLista').innerHTML = '';
    document.getElementById('ativarInstrucao').textContent =
        'Verificando duplicidades...';

    if (!doctorId) {
        doctorId = window.currentDoctorId;
        window._ativarCtx.doctorId = doctorId;
    }

    // Verifica requisitos e duplicidades sem ativar o cadastro.
    fetch(`/api/patients/${patientId}/activation-preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        body: JSON.stringify({ doctor_id: doctorId, phone: existingPhone })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            document.getElementById('ativarInstrucao').textContent =
                'Revise os dados e confirme para ativar como novo paciente definitivo.';
            return;
        }
        if (data.error === 'phone_required' || data.warning === 'phone_required') {
            document.getElementById('ativarInstrucao').textContent =
                data.message || 'Informe o telefone do paciente e escolha uma opção para ativar.';
            return;
        }
        if (data.warning === 'duplicates_found') {
            renderActivationWarnings(data, patientId, doctorId);
        } else if (data.error) {
            showAlert(data.error, 'danger');
        }
    })
    .catch(() => showAlert('Erro ao verificar duplicados', 'danger'));

    const modal = new bootstrap.Modal(document.getElementById('ativarProvisiorioModal'));
    modal.show();

    document.getElementById('ativarDiretoBtn').onclick = function() {
        const ctx = window._ativarCtx;
        const phone = document.getElementById('ativarTelefonePaciente').value.trim();
        if (!phone) {
            document.getElementById('ativarTelefoneErro').classList.remove('d-none');
            telInput.focus();
            return;
        }
        document.getElementById('ativarTelefoneErro').classList.add('d-none');
        const forceActivation = (ctx.warnings || []).length > 0;
        _finalizarAtivacao(ctx.patientId, ctx.doctorId, null, forceActivation, phone);
    };
};

window._finalizarAtivacao = function(patientId, doctorId, mergeIntoId, force, phone) {
    const payload = { doctor_id: doctorId, force: !!force };
    if (mergeIntoId) payload.merge_into_patient_id = mergeIntoId;
    if (phone) payload.phone = phone;

    fetch(`/api/patients/${patientId}/ativar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
	    .then(data => {
	        if (data.success) {
	            const action = data.action === 'merge' ? 'vinculado ao cadastro existente' : 'ativado';
	            showAlert(`Cadastro ${action} com sucesso! Código: ${data.patient_code}`, 'success');
	            const modal = bootstrap.Modal.getInstance(document.getElementById('ativarProvisiorioModal'));
	            if (modal) modal.hide();
	            loadAppointments();
	        } else if (data.warning === 'duplicates_found') {
	            renderActivationWarnings(data, patientId, doctorId);
	        } else {
	            showAlert(data.error || 'Erro ao ativar cadastro', 'danger');
	        }
    })
    .catch(() => showAlert('Erro ao ativar cadastro', 'danger'));
};
