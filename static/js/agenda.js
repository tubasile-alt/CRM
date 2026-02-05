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
        const cleanString = isoString.replace(/[+-]\d{2}:\d{2}$/, '').replace('Z', '');
        const [datePart, timePart] = cleanString.split('T');
        const [year, month, day] = datePart.split('-').map(Number);
        const timeParts = timePart ? timePart.split(':') : ['00', '00', '00'];
        const [hours, minutes, seconds] = timeParts.map(s => parseFloat(s));
        return new Date(year, month - 1, day, hours, Math.floor(minutes), Math.floor(seconds));
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
        }
        initializeDayView();
        initializeMonthCalendar();
        loadAppointments();
        updateWaitingCounter();
        setInterval(updateWaitingCounter, 30000);
        renderMiniCalendar();
        setupPatientAutocomplete();
        startWaitingRoomUpdates();
        setupWebcamHandlers();
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
            let doctorId = '';
            if (window.isSecretary && document.getElementById('appointmentDoctor')) {
                doctorId = document.getElementById('appointmentDoctor').value || '';
            }
            const url = doctorId 
                ? `/api/patients/search?q=${encodeURIComponent(query)}&doctor_id=${doctorId}`
                : `/api/patients/search?q=${encodeURIComponent(query)}`;
            
            fetch(url)
                .then(r => r.json())
                .then(patients => {
                    suggestionsDiv.innerHTML = '';
                    if (!Array.isArray(patients) || patients.length === 0) {
                        suggestionsDiv.style.display = 'none';
                        return;
                    }
                    patients.forEach(patient => {
                        const div = document.createElement('div');
                        div.className = 'p-2 border-bottom cursor-pointer hover-bg-light';
                        div.style.cursor = 'pointer';
                        const code = patient.patient_code ? `(${patient.patient_code})` : '';
                        div.textContent = `${patient.name} ${code}`;
                        div.onclick = () => selectPatient(patient);
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
        document.getElementById('patientCPF').value = patient.cpf || '';
        document.getElementById('patientBirthDate').value = patient.birth_date || '';
        document.getElementById('patientPhone').value = patient.phone || '';
        document.getElementById('patientAddress').value = patient.address || '';
        document.getElementById('patientCity').value = patient.city || '';
        document.getElementById('patientMotherName').value = patient.mother_name || '';
        document.getElementById('patientIndicationSource').value = patient.indication_source || '';
        document.getElementById('patientOccupation').value = patient.occupation || '';
        document.getElementById('patientType').value = patient.patient_type || 'particular';
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

    window.initializeDayView = function() {
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
            'Botox': 'appointment-botox',
            'Laser': 'appointment-laser',
            'Preenchimento': 'appointment-preenchimento'
        };
        return typeMap[type] || 'appointment-particular';
    }

    window.renderDayView = function() {
        const appointmentsGrid = document.getElementById('appointmentsGrid');
        if (!appointmentsGrid) return;
        appointmentsGrid.innerHTML = '';
        
        const dayAppointments = appointmentsList.filter(app => {
            const appDateStr = app.start.split('T')[0];
            const selectedDateStr = selectedDate.getFullYear() + '-' + 
                                   String(selectedDate.getMonth() + 1).padStart(2, '0') + '-' + 
                                   String(selectedDate.getDate()).padStart(2, '0');
            const doctorMatch = !currentDoctorFilter || app.extendedProps?.doctorId == currentDoctorFilter;
            return appDateStr === selectedDateStr && doctorMatch;
        });
        
        if (dayAppointments.length === 0) {
            appointmentsGrid.innerHTML = '<div class="empty-schedule">Nenhum agendamento para este dia</div>';
            return;
        }

        dayAppointments.sort((a, b) => {
            const startA = parseLocalDateTime(a.start);
            const startB = parseLocalDateTime(b.start);
            return startA - startB;
        });

        dayAppointments.forEach(app => {
            const start = parseLocalDateTime(app.start);
            const timeStr = String(start.getHours()).padStart(2, '0') + ':' + String(start.getMinutes()).padStart(2, '0');
            const patientName = app.title ? app.title.split(' - ')[0] : 'Paciente';
            const appointmentType = app.extendedProps?.appointmentType || app.appointmentType || 'Particular';
            const patientType = app.extendedProps?.patientType || app.patientType || 'Particular';
            const patientCode = app.extendedProps?.patientCode || '-';
            const status = app.extendedProps?.status || app.status || 'agendado';
            const typeClass = getAppointmentTypeClass(appointmentType);
            const statusClass = `status-${status}`;
            const patientId = app.extendedProps?.patientId || app.patientId;

            const block = document.createElement('div');
            block.className = `appointment-block ${typeClass} ${statusClass}`;
            block.style.cursor = 'pointer';
            block.dataset.appointmentId = app.id;

            const isWaiting = app.extendedProps?.waiting || app.waiting || false;
            let actionBadgeHtml = '';
            
            if (status === 'atendido') {
                actionBadgeHtml = `<span class="atendido-badge"><i class="bi bi-check-circle-fill"></i> ATENDIDO</span>`;
            } else if (status === 'faltou') {
                actionBadgeHtml = `<span class="faltou-badge"><i class="bi bi-x-circle-fill"></i> FALTOU</span>
                    <button class="checkin-btn ms-2" onclick="event.stopPropagation(); doCheckin(${app.id})" title="Chegou atrasado - Fazer Check-in"><i class="bi bi-box-arrow-in-right"></i> Check In</button>`;
            } else if (isWaiting) {
                actionBadgeHtml = `
                    <span class="waiting-badge"><i class="bi bi-hourglass-split"></i> Aguardando</span>
                    <button class="btn btn-sm btn-success ms-2" onclick="event.stopPropagation(); doCheckout(${app.id})" title="Finalizar atendimento">
                        <i class="bi bi-check2-circle"></i> Finalizar
                    </button>
                    <button class="btn btn-sm btn-outline-danger ms-1" onclick="event.stopPropagation(); removeFromWaiting(${app.id})" title="Remover da espera (sem finalizar)">
                        <i class="bi bi-x-circle"></i> Remover
                    </button>
                `;
            } else {
                actionBadgeHtml = `<button class="checkin-btn" onclick="event.stopPropagation(); doCheckin(${app.id})" title="Fazer Check-in"><i class="bi bi-box-arrow-in-right"></i> Check In</button>`;
            }

            block.innerHTML = `
                <div class="appointment-content">
                    <div class="appointment-info-line">
                        <span class="appointment-time-badge">${timeStr}</span>
                        <span class="appointment-name" onclick="event.stopPropagation(); goToPatientChart(${patientId}, ${app.id})" style="cursor:pointer; text-decoration:underline;">${patientName}</span>
                        <span class="appointment-code">cod:${patientCode}</span>
                        <span class="appointment-type-label">pac:${patientType}</span>
                        <span class="appointment-consult-label">cons:${appointmentType}</span>
                        ${actionBadgeHtml}
                    </div>
                </div>
            `;

            block.onclick = () => selectAppointment(app);
            appointmentsGrid.appendChild(block);
        });
    };

    window.goToPatientChart = function(patientId, appointmentId) {
        if (patientId) {
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

    window.loadAppointments = function() {
        let url = `/api/appointments?date=${selectedDate.toISOString().split('T')[0]}`;
        if (currentDoctorFilter) url += `&doctor_id=${currentDoctorFilter}`;
        fetch(url).then(r => r.json()).then(events => {
            appointmentsList = events;
            renderDayView();
            if (calendar) calendar.refetchEvents();
        });
    };

    window.selectDate = function(date) {
        selectedDate = new Date(date);
        renderMiniCalendar();
        initializeDayView();
        loadAppointments();
    };

    window.previousMonth = function() { selectedDate.setMonth(selectedDate.getMonth() - 1); renderMiniCalendar(); };
    window.nextMonth = function() { selectedDate.setMonth(selectedDate.getMonth() + 1); renderMiniCalendar(); };
    window.previousDay = function() { selectedDate.setDate(selectedDate.getDate() - 1); selectDate(selectedDate); };
    window.nextDay = function() { selectedDate.setDate(selectedDate.getDate() + 1); selectDate(selectedDate); };
    window.todayDay = function() { selectDate(new Date()); };

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
        document.getElementById('editPatientName').value = app.title.split(' - ')[0];
        const start = parseLocalDateTime(app.start);
        document.getElementById('editAppointmentDate').value = start.toISOString().split('T')[0];
        document.getElementById('editAppointmentTime').value = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`;
        
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
        fetch(`/api/patients/search_detailed?q=${encodeURIComponent(q)}`)
            .then(r => r.json())
            .then(data => {
                body.innerHTML = data.length ? data.map(p => `
                    <tr>
                        <td>${p.name}</td>
                        <td>${p.prontuario}</td>
                        <td>${p.last_consult}</td>
                        <td><button class="btn btn-sm btn-primary" onclick="openPatientDetail(${p.id})">Ficha</button></td>
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

    function loadWaitingRoom() {
        fetch('/espera/api/list').then(r => r.json()).then(d => {
            const list = document.getElementById('waitingRoomList');
            if (!list) return;
            const items = d.waiting_list || [];
            waitingRoomData = items;
            list.innerHTML = items.length ? items.map(p => `
                <div class="waiting-patient-item" onclick="goToPatientChart(${p.patient_id}, ${p.appointment_id})" style="cursor:pointer; padding: 8px; border-bottom: 1px solid #eee; transition: background 0.2s;">
                    <div class="d-flex justify-content-between align-items-center">
                        <span style="font-weight: 500;">${p.patient_name}</span>
                        <small class="text-muted">(${p.wait_time || '0 min'})</small>
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

    window.saveAppointment = function() {
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
            patient_id: patientId || null,
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

        fetch('/api/appointments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showAlert('Agendamento salvo com sucesso!');
                loadAppointments();
                const modal = bootstrap.Modal.getInstance(document.getElementById('newAppointmentModal'));
                if (modal) modal.hide();
                
                // Limpar formulário
                const form = document.getElementById('appointmentForm');
                if (form) form.reset();
                
                const idsToClear = ['selectedPatientId', 'patientPhotoData'];
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
        const patientType = document.getElementById('editPatientType')?.value || 'Particular';
        const appointmentType = document.getElementById('editAppointmentType')?.value || 'Particular';
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
            patientType: patientType,
            appointmentType: appointmentType,
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
