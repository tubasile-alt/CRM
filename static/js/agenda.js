let calendar;
let currentEvent = null;

document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'pt-br',
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        buttonText: {
            today: 'Hoje',
            month: 'Mês',
            week: 'Semana',
            day: 'Dia',
            list: 'Lista'
        },
        height: 'auto',
        navLinks: true,
        editable: true,
        selectable: true,
        selectMirror: true,
        dayMaxEvents: true,
        datesSet: function(info) {
            // Carregar eventos sem filtro de data para mostrar histórico completo
        },
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
        },
        
        eventDrop: function(info) {
            updateEventTime(info.event);
        },
        
        eventResize: function(info) {
            updateEventTime(info.event);
        },
        
        select: function(info) {
            document.getElementById('appointmentStart').value = info.startStr.slice(0, 16);
            const modal = new bootstrap.Modal(document.getElementById('newAppointmentModal'));
            modal.show();
        }
    });
    
    calendar.render();
});

function saveAppointment() {
    const patientName = document.getElementById('patientName').value;
    const phone = document.getElementById('patientPhone').value;
    const patientType = document.getElementById('patientType').value;
    const start = document.getElementById('appointmentStart').value;
    const duration = parseInt(document.getElementById('appointmentDuration').value);
    const status = document.getElementById('appointmentStatus').value;
    const appointmentType = document.getElementById('appointmentType').value;
    const notes = document.getElementById('appointmentNotes').value;
    
    // Get doctor_id if secretary is creating appointment
    const doctorSelect = document.getElementById('appointmentDoctor');
    const doctorId = doctorSelect ? parseInt(doctorSelect.value) : null;
    
    if (!patientName || !start) {
        showAlert('Por favor, preencha os campos obrigatórios.', 'danger');
        return;
    }
    
    const startDate = new Date(start);
    const endDate = new Date(startDate.getTime() + duration * 60000);
    
    const payload = {
        patientName: patientName,
        phone: phone,
        patientType: patientType,
        start: startDate.toISOString(),
        end: endDate.toISOString(),
        status: status,
        appointmentType: appointmentType,
        notes: notes
    };
    
    // Include doctor_id for secretaries
    if (doctorId) {
        payload.doctor_id = doctorId;
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
            calendar.refetchEvents();
            bootstrap.Modal.getInstance(document.getElementById('newAppointmentModal')).hide();
            document.getElementById('appointmentForm').reset();
        }
    })
    .catch(error => {
        showAlert('Erro ao criar agendamento.', 'danger');
        console.error(error);
    });
}

function updateEventTime(event) {
    fetch(`/api/appointments/${event.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            start: event.start.toISOString(),
            end: event.end.toISOString()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Horário atualizado com sucesso!');
        }
    })
    .catch(error => {
        showAlert('Erro ao atualizar horário.', 'danger');
        console.error(error);
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
    
    // Check if user is secretary
    const isSecretary = window.isSecretary === true;
    
    let detailsHtml = '';
    
    if (isSecretary) {
        // Secretary view - editable fields
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
        // Doctor view - read-only
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
    
    // Update modal footer buttons
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
        document.getElementById('checkinButtons').style.display = 'none';
    } else {
        if (saveBtn) saveBtn.remove();
        document.getElementById('checkinButtons').style.display = 'block';
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
            calendar.refetchEvents();
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
            calendar.refetchEvents();
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
            calendar.refetchEvents();
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
