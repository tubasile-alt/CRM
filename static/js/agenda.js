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
            fetch('/api/appointments')
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
    const statusLabels = {
        'agendado': 'Agendado',
        'confirmado': 'Confirmado',
        'atendido': 'Atendido',
        'faltou': 'Faltou'
    };
    
    const detailsHtml = `
        <p><strong>Paciente:</strong> ${event.title}</p>
        <p><strong>Data/Hora:</strong> ${formatDateTime(event.start)}</p>
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
            <button class="btn btn-sm btn-info mt-2" onclick="openPatientChart()">
                <i class="bi bi-file-text"></i> Abrir Prontuário
            </button>
        </div>
    `;
    
    document.getElementById('eventDetails').innerHTML = detailsHtml;
    const modal = new bootstrap.Modal(document.getElementById('eventDetailModal'));
    modal.show();
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
