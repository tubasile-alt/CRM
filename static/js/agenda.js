(function() {
    let appointmentsList = [];
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
            webcamStream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (video) {
                video.srcObject = webcamStream;
                video.style.display = 'block';
            }
            if (placeholder) placeholder.style.display = 'none';
            if (startBtn) startBtn.style.display = 'none';
            if (captureBtn) captureBtn.style.display = 'inline-block';
        } catch (err) {
            console.error("Erro webcam:", err);
            alert("Não foi possível acessar a câmera.");
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
            const id = e.target.id || e.target.closest('button')?.id;
            if (id === 'start-webcam-btn') startWebcam('webcam-video', 'webcam-placeholder', 'start-webcam-btn', 'capture-photo-btn');
            if (id === 'capture-photo-btn') capturePhoto('webcam-video', 'photo-canvas', 'patient-photo-preview', 'capture-photo-btn', 'retake-photo-btn', 'patientPhotoData');
            if (id === 'retake-photo-btn') {
                const preview = document.getElementById('patient-photo-preview');
                if (preview) preview.style.display = 'none';
                startWebcam('webcam-video', 'webcam-placeholder', 'start-webcam-btn', 'capture-photo-btn');
            }
        });
    }

    window.initializeDayView = function() {
        const scheduleDate = document.getElementById('scheduleDate');
        if (scheduleDate) scheduleDate.textContent = formatDateBR(selectedDate);
        renderTimeColumn();
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
                slot.onclick = () => openNewAppointmentAtTime(hour, minutes);
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

    window.renderDayView = function() {
        const grid = document.getElementById('appointmentsGrid');
        if (!grid) return;
        grid.innerHTML = '';
        const dateStr = selectedDate.toISOString().split('T')[0];
        const filtered = appointmentsList.filter(a => a.start.startsWith(dateStr) && (!currentDoctorFilter || a.extendedProps?.doctorId == currentDoctorFilter));
        
        if (filtered.length === 0) {
            grid.innerHTML = '<div class="empty-schedule">Nenhum agendamento</div>';
            return;
        }

        filtered.sort((a, b) => a.start.localeCompare(b.start)).forEach(app => {
            const start = parseLocalDateTime(app.start);
            const timeStr = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`;
            const patientName = app.title.split(' - ')[0];
            const block = document.createElement('div');
            block.className = `appointment-block appointment-${(app.extendedProps?.appointmentType || 'particular').toLowerCase().replace(/\s+/g, '-')}`;
            block.innerHTML = `<div class="appointment-info-line"><b>${timeStr}</b> ${patientName}</div>`;
            block.onclick = () => selectAppointment(app);
            grid.appendChild(block);
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
        if (window.isSecretary) openEditAppointmentModal(app);
        else showEventDetails(app);
    }

    function openEditAppointmentModal(app) {
        const modalEl = document.getElementById('editAppointmentModal');
        if (!modalEl) return;
        document.getElementById('editAppointmentId').value = app.id;
        document.getElementById('editPatientName').value = app.title.split(' - ')[0];
        const start = parseLocalDateTime(app.start);
        document.getElementById('editAppointmentDate').value = start.toISOString().split('T')[0];
        document.getElementById('editAppointmentTime').value = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`;
        new bootstrap.Modal(modalEl).show();
    }

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
            list.innerHTML = items.length ? items.map(p => `<div class="waiting-patient-item">${p.patient_name}</div>`).join('') : '<div class="waiting-empty">Vazio</div>';
        });
    }

    function openNewAppointmentAtTime(h, m) {
        const date = selectedDate.toISOString().split('T')[0];
        document.getElementById('appointmentDate').value = date;
        document.getElementById('appointmentTime').value = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
        new bootstrap.Modal(document.getElementById('newAppointmentModal')).show();
    }

    function formatDateBR(date) {
        const days = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];
        const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        return `${days[date.getDay()]}, ${date.getDate()} de ${months[date.getMonth()]} de ${date.getFullYear()}`;
    }

    window.showEventDetails = function(event) {
        const props = event.extendedProps;
        const patientName = event.title.split(' - ')[0];
        
        function formatToLocalDateTime(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}`;
        }
        
        const startDateTime = formatToLocalDateTime(event.start);
        const endDateTime = formatToLocalDateTime(event.end);
        
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
                    <input type="text" class="form-control" id="editPatientName" value="${patientName}">
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Data/Hora Início</strong></label>
                    <input type="datetime-local" class="form-control" id="editStartTime" value="${startDateTime}">
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Data/Hora Fim</strong></label>
                    <input type="datetime-local" class="form-control" id="editEndTime" value="${endDateTime}">
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Telefone</strong></label>
                    <input type="tel" class="form-control" id="editPhone" value="${props.phone || ''}">
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Tipo de Consulta</strong></label>
                    <select class="form-select" id="editAppointmentType">
                        ${appointmentTypes.map(type => `<option value="${type}" ${props.appointmentType === type ? 'selected' : ''}>${type}</option>`).join('')}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Status</strong></label>
                    <select class="form-select" id="editStatus">
                        <option value="agendado" ${props.status === 'agendado' ? 'selected' : ''}>Agendado</option>
                        <option value="confirmado" ${props.status === 'confirmado' ? 'selected' : ''}>Confirmado</option>
                        <option value="atendido" ${props.status === 'atendido' ? 'selected' : ''}>Atendido</option>
                        <option value="faltou" ${props.status === 'faltou' ? 'selected' : ''}>Faltou</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label"><strong>Observações</strong></label>
                    <textarea class="form-control" id="editNotes" rows="3">${props.notes || ''}</textarea>
                </div>
            `;
        } else {
            const appointmentType = props.appointmentType || 'Particular';
            const status = props.status || 'agendado';
            detailsHtml = `
                <p><strong>Paciente:</strong> ${patientName}</p>
                <p><strong>Data/Hora:</strong> ${formatDateTime(event.start)}</p>
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
        const startStr = document.getElementById('editStartTime').value;
        const endStr = document.getElementById('editEndTime').value;
        const payload = {
            patientName: document.getElementById('editPatientName').value,
            start: startStr + ':00',
            end: endStr + ':00',
            phone: document.getElementById('editPhone').value,
            appointmentType: document.getElementById('editAppointmentType').value,
            status: document.getElementById('editStatus').value,
            notes: document.getElementById('editNotes').value
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
        let patientId = currentEvent.extendedProps?.patientId || currentEvent.extendedProps?.extendedProps?.patientId;
        if (patientId) {
            window.location.href = `/prontuario/${patientId}?appointment_id=${currentEvent.id}`;
        }
    };

    function formatDateTime(date) {
        const d = new Date(date);
        return d.toLocaleDateString('pt-BR') + ' ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
    }

    window.filterByDoctor = function(doctorId) {
        currentDoctorFilter = doctorId === 'all' ? null : doctorId;
        loadAppointments();
        if (calendar) calendar.refetchEvents();
    };

    window.switchView = function(view) {
        currentView = view;
        const dayContent = document.getElementById('dayViewContent');
        const monthContent = document.getElementById('monthViewContent');
        const dayBtn = document.getElementById('dayViewBtn');
        const monthBtn = document.getElementById('monthViewBtn');
        
        if (view === 'day') {
            dayContent.style.display = 'grid';
            monthContent.style.display = 'none';
            dayBtn.classList.add('active');
            monthBtn.classList.remove('active');
        } else {
            dayContent.style.display = 'none';
            monthContent.style.display = 'block';
            dayBtn.classList.remove('active');
            monthBtn.classList.add('active');
            if (!calendar) initializeMonthCalendar();
        }
    };

})();
