let appointmentsList = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeDayView();
    initializeMonthCalendar();
    loadAppointments();
    updateWaitingCounter();
    setInterval(updateWaitingCounter, 30000);
    renderMiniCalendar();
    renderDayView();
});

function initializeDayView() {
    document.getElementById('scheduleDate').textContent = formatDateBR(selectedDate);
    renderTimeColumn();
}

function renderTimeColumn() {
    const timeColumn = document.getElementById('timeColumn');
    timeColumn.innerHTML = '';
    for (let hour = 7; hour <= 19; hour++) {
        const slot = document.createElement('div');
        slot.className = 'hour-slot';
        slot.textContent = String(hour).padStart(2, '0') + ':00';
        timeColumn.appendChild(slot);
    }
}

function renderMiniCalendar() {
    const miniCalendar = document.getElementById('miniCalendar');
    const today = new Date();
    const currentMonth = selectedDate.getMonth();
    const currentYear = selectedDate.getFullYear();
    
    let html = `
        <div class="mini-calendar-header">
            <button onclick="previousMonth()"><i class="bi bi-chevron-left"></i></button>
            <div style="font-size: 14px; font-weight: 600; min-width: 120px; text-align: center;">
                ${new Date(currentYear, currentMonth).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
            </div>
            <button onclick="nextMonth()"><i class="bi bi-chevron-right"></i></button>
        </div>
        <div class="mini-calendar-grid">
            <div class="mini-calendar-day">Dom</div>
            <div class="mini-calendar-day">Seg</div>
            <div class="mini-calendar-day">Ter</div>
            <div class="mini-calendar-day">Qua</div>
            <div class="mini-calendar-day">Qui</div>
            <div class="mini-calendar-day">Sex</div>
            <div class="mini-calendar-day">Sab</div>
    `;
    
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    for (let i = 0; i < firstDay; i++) {
        html += '<div class="mini-calendar-date" style="color: #ccc;"></div>';
    }
    
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(currentYear, currentMonth, day);
        const isSelected = date.toDateString() === selectedDate.toDateString();
        const isToday = date.toDateString() === today.toDateString();
        
        html += `
            <div class="mini-calendar-date ${isSelected ? 'selected' : ''} ${isToday ? 'today' : ''}" 
                 onclick="selectDate(new Date(${currentYear}, ${currentMonth}, ${day}))">
                ${day}
            </div>
        `;
    }
    
    html += '</div>';
    miniCalendar.innerHTML = html;
}

function renderDayView() {
    const appointmentsGrid = document.getElementById('appointmentsGrid');
    appointmentsGrid.innerHTML = '';
    
    const dayAppointments = appointmentsList.filter(app => {
        const appDate = new Date(app.start).toDateString();
        return appDate === selectedDate.toDateString() && (!currentDoctorFilter || app.doctor_id == currentDoctorFilter);
    });
    
    if (dayAppointments.length === 0) {
        appointmentsGrid.innerHTML = '<div class="empty-schedule">Nenhum agendamento para este dia</div>';
        return;
    }
    
    dayAppointments.forEach(app => {
        const start = new Date(app.start);
        const end = new Date(app.end);
        const durationMinutes = (end - start) / (1000 * 60);
        const topPosition = ((start.getHours() - 7) * 60 + start.getMinutes()) * 1;
        const height = durationMinutes;
        
        // Extrair apenas o nome do paciente (sem nome do médico)
        const patientName = app.title ? app.title.split(' - ')[0] : 'Paciente';
        
        const appointmentType = app.extendedProps?.appointmentType || app.appointmentType || 'Particular';
        const patientType = app.extendedProps?.patientType || app.patientType || 'Particular';
        const status = app.extendedProps?.status || app.status || 'agendado';
        const typeClass = getAppointmentTypeClass(appointmentType);
        const statusClass = `status-${status}`;
        
        const block = document.createElement('div');
        block.className = `appointment-block ${typeClass} ${statusClass}`;
        block.style.top = topPosition + 'px';
        block.style.height = Math.max(height, 50) + 'px';
        block.onclick = () => selectAppointment(app);
        
        block.innerHTML = `
            <div class="appointment-content">
                <div class="appointment-name">${patientName}</div>
                <div class="appointment-row">
                    <div class="appointment-cell appointment-patient-type"><strong>Pac:</strong> ${patientType}</div>
                    <div class="appointment-cell appointment-consult-type"><strong>Cons:</strong> ${appointmentType}</div>
                </div>
            </div>
        `;
        
        appointmentsGrid.appendChild(block);
    });
}

function getAppointmentTypeClass(type) {
    if (!type) return 'appointment-particular';
    if (type.includes('Transplante')) return 'appointment-transplante';
    if (type.includes('Particular')) return 'appointment-particular';
    if (type.includes('Retorno')) return 'appointment-retorno';
    if (type.includes('UNIMED')) return 'appointment-unimed';
    if (type.includes('Cortesia')) return 'appointment-cortesia';
    return 'appointment-particular';
}

function selectDate(date) {
    selectedDate = new Date(date);
    renderMiniCalendar();
    renderDayView();
    document.getElementById('scheduleDate').textContent = formatDateBR(selectedDate);
}

function selectAppointment(app) {
    currentEvent = {
        id: app.id,
        title: app.title,
        start: new Date(app.start),
        end: new Date(app.end),
        extendedProps: app
    };
    showEventDetails(currentEvent);
}

function previousDay() {
    selectedDate.setDate(selectedDate.getDate() - 1);
    selectDate(new Date(selectedDate));
}

function nextDay() {
    selectedDate.setDate(selectedDate.getDate() + 1);
    selectDate(new Date(selectedDate));
}

function todayDay() {
    selectDate(new Date());
}

function previousMonth() {
    selectedDate.setMonth(selectedDate.getMonth() - 1);
    renderMiniCalendar();
}

function nextMonth() {
    selectedDate.setMonth(selectedDate.getMonth() + 1);
    renderMiniCalendar();
}

function switchView(view) {
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
}

function initializeMonthCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'pt-br',
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: ''
        },
        buttonText: {
            today: 'Hoje'
        },
        height: 'auto',
        navLinks: true,
        editable: false,
        events: function(info, successCallback, failureCallback) {
            let url = '/api/appointments';
            if (currentDoctorFilter) {
                url += `?doctor_id=${currentDoctorFilter}`;
            }
            fetch(url)
                .then(r => r.json())
                .then(events => successCallback(events))
                .catch(err => failureCallback(err));
        },
        eventClick: function(info) {
            currentEvent = info.event;
            showEventDetails(info.event);
        }
    });
    
    calendar.render();
}

function loadAppointments() {
    let url = '/api/appointments';
    if (currentDoctorFilter) {
        url += `?doctor_id=${currentDoctorFilter}`;
    }
    
    fetch(url)
        .then(r => r.json())
        .then(events => {
            appointmentsList = events;
            renderDayView();
            if (calendar) calendar.refetchEvents();
        });
}

function formatDateBR(date) {
    const days = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];
    const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    return `${days[date.getDay()]}, ${date.getDate()} de ${months[date.getMonth()]} de ${date.getFullYear()}`;
}

function formatDateTime(date) {
    const d = new Date(date);
    return d.toLocaleDateString('pt-BR') + ' ' + d.getHours().toString().padStart(2, '0') + ':' + d.getMinutes().toString().padStart(2, '0');
}

function filterByDoctor(doctorId) {
    currentDoctorFilter = doctorId === 'all' ? null : doctorId;
    loadAppointments();
    if (calendar) calendar.refetchEvents();
    
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

function updateWaitingCounter() {
    fetch('/espera/api/stats')
        .then(r => r.json())
        .then(stats => {
            document.getElementById('waitingCount').textContent = stats.count || 0;
        });
}

function showEventDetails(event) {
    const props = event.extendedProps;
    const patientName = event.title.split(' - ')[0];
    const startDateTime = event.start.toISOString().slice(0, 16);
    const endDateTime = event.end.toISOString().slice(0, 16);
    
    const statusLabels = {
        'agendado': 'Agendado',
        'confirmado': 'Confirmado',
        'atendido': 'Atendido',
        'faltou': 'Faltou'
    };
    
    const appointmentTypes = ['Particular', 'Transplante Capilar', 'Retorno', 'UNIMED', 'Cortesia'];
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
        detailsHtml = `
            <p><strong>Paciente:</strong> ${patientName}</p>
            <p><strong>Data/Hora:</strong> ${formatDateTime(event.start)}</p>
            <p><strong>Tipo:</strong> ${props.appointmentType}</p>
            <p><strong>Status:</strong> <span class="badge bg-secondary">${statusLabels[props.status]}</span></p>
            ${props.phone ? `<p><strong>Telefone:</strong> ${props.phone}</p>` : ''}
            ${props.notes ? `<p><strong>Observações:</strong> ${props.notes}</p>` : ''}
            <div class="mt-3">
                <label class="form-label">Alterar Status:</label>
                <select class="form-select" id="eventStatusUpdate">
                    <option value="agendado" ${props.status === 'agendado' ? 'selected' : ''}>Agendado</option>
                    <option value="confirmado" ${props.status === 'confirmado' ? 'selected' : ''}>Confirmado</option>
                    <option value="atendido" ${props.status === 'atendido' ? 'selected' : ''}>Atendido</option>
                    <option value="faltou" ${props.status === 'faltou' ? 'selected' : ''}>Faltou</option>
                </select>
                <button class="btn btn-sm btn-primary mt-2" onclick="updateEventStatus()">Atualizar Status</button>
            </div>
        `;
    }
    
    document.getElementById('eventDetails').innerHTML = detailsHtml;
    
    const footer = document.querySelector('#eventDetailModal .modal-footer');
    let saveBtn = document.getElementById('saveEditBtn');
    
    if (isSecretary) {
        if (!saveBtn) {
            saveBtn = document.createElement('button');
            saveBtn.id = 'saveEditBtn';
            saveBtn.type = 'button';
            saveBtn.className = 'btn btn-success';
            saveBtn.innerHTML = '<i class="bi bi-save"></i> Salvar Alterações';
            saveBtn.onclick = saveAppointmentEdits;
            footer.insertBefore(saveBtn, footer.firstChild);
        }
    } else {
        if (saveBtn) saveBtn.remove();
    }
    
    const modal = new bootstrap.Modal(document.getElementById('eventDetailModal'));
    modal.show();
}

function saveAppointmentEdits() {
    const payload = {
        patientName: document.getElementById('editPatientName').value,
        start: document.getElementById('editStartTime').value + ':00',
        end: document.getElementById('editEndTime').value + ':00',
        phone: document.getElementById('editPhone').value,
        appointmentType: document.getElementById('editAppointmentType').value,
        status: document.getElementById('editStatus').value,
        notes: document.getElementById('editNotes').value
    };
    
    if (!payload.patientName || !payload.start || !payload.end) {
        showAlert('Por favor, preencha os campos obrigatórios', 'danger');
        return;
    }
    
    fetch(`/api/appointments/${currentEvent.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Agendamento atualizado com sucesso!');
            loadAppointments();
            bootstrap.Modal.getInstance(document.getElementById('eventDetailModal')).hide();
        } else {
            showAlert(data.error || 'Erro ao atualizar agendamento', 'danger');
        }
    })
    .catch(error => {
        showAlert('Erro ao salvar alterações', 'danger');
        console.error(error);
    });
}

function updateEventStatus() {
    const newStatus = document.getElementById('eventStatusUpdate').value;
    
    fetch(`/api/appointments/${currentEvent.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: newStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Status atualizado com sucesso!');
            loadAppointments();
            bootstrap.Modal.getInstance(document.getElementById('eventDetailModal')).hide();
        }
    })
    .catch(error => {
        showAlert('Erro ao atualizar status.', 'danger');
        console.error(error);
    });
}

function deleteEvent() {
    if (!confirm('Tem certeza que deseja excluir este agendamento?')) {
        return;
    }
    
    fetch(`/api/appointments/${currentEvent.id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Agendamento excluído com sucesso!');
            loadAppointments();
            bootstrap.Modal.getInstance(document.getElementById('eventDetailModal')).hide();
        }
    })
    .catch(error => {
        showAlert('Erro ao excluir agendamento.', 'danger');
        console.error(error);
    });
}

function openPatientChart() {
    if (currentEvent && currentEvent.extendedProps.patientId) {
        const appointmentId = currentEvent.id;
        window.location.href = `/prontuario/${currentEvent.extendedProps.patientId}?appointment_id=${appointmentId}`;
    }
}

function saveAppointment() {
    const patientName = document.getElementById('patientName').value;
    const phone = document.getElementById('patientPhone').value;
    const start = document.getElementById('appointmentStart').value;
    const duration = parseInt(document.getElementById('appointmentDuration').value);
    const status = document.getElementById('appointmentStatus').value;
    const appointmentType = document.getElementById('appointmentType').value;
    const notes = document.getElementById('appointmentNotes').value;
    
    let doctor_id = null;
    if (window.isSecretary) {
        doctor_id = document.getElementById('appointmentDoctor').value;
    }
    
    const startDate = new Date(start);
    const endDate = new Date(startDate.getTime() + duration * 60000);
    
    const payload = {
        title: patientName,
        phone: phone,
        start: startDate.toISOString(),
        end: endDate.toISOString(),
        status: status,
        appointmentType: appointmentType,
        notes: notes
    };
    
    if (doctor_id) {
        payload.doctor_id = doctor_id;
    }
    
    fetch('/api/appointments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Agendamento criado com sucesso!');
            loadAppointments();
            bootstrap.Modal.getInstance(document.getElementById('newAppointmentModal')).hide();
            document.getElementById('appointmentForm').reset();
        } else {
            showAlert(data.error || 'Erro ao criar agendamento', 'danger');
        }
    })
    .catch(error => {
        showAlert('Erro ao salvar agendamento', 'danger');
        console.error(error);
    });
}

function exportAgenda(format) {
    const start = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1).toISOString().split('T')[0];
    const end = new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 0).toISOString().split('T')[0];
    
    let url = `/agenda/export/${format}?start=${start}&end=${end}`;
    if (currentDoctorFilter) {
        url += `&doctor_id=${currentDoctorFilter}`;
    }
    window.location.href = url;
}

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 3000);
}

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}
