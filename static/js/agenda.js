let appointmentsList = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeDayView();
    initializeMonthCalendar();
    loadAppointments();
    updateWaitingCounter();
    setInterval(updateWaitingCounter, 30000);
    renderMiniCalendar();
    renderDayView();
    setupPatientAutocomplete();
});

function setupPatientAutocomplete() {
    const patientInput = document.getElementById('patientName');
    const suggestionsDiv = document.getElementById('patientSuggestions');
    
    patientInput.addEventListener('input', function() {
        const query = this.value.trim();
        if (query.length < 2) {
            suggestionsDiv.style.display = 'none';
            return;
        }
        
        let doctorId = null;
        if (window.isSecretary && document.getElementById('appointmentDoctor')) {
            doctorId = document.getElementById('appointmentDoctor').value;
        }
        
        fetch(`/api/patients/search?q=${encodeURIComponent(query)}&doctor_id=${doctorId}`)
            .then(r => r.json())
            .then(patients => {
                suggestionsDiv.innerHTML = '';
                if (patients.length === 0) {
                    suggestionsDiv.style.display = 'none';
                    return;
                }
                
                patients.forEach(patient => {
                    const div = document.createElement('div');
                    div.className = 'p-2 border-bottom cursor-pointer';
                    div.style.cursor = 'pointer';
                    const code = patient.patient_code ? `(${patient.patient_code})` : '';
                    div.textContent = `${patient.name} ${code}`;
                    div.onclick = () => selectPatient(patient);
                    suggestionsDiv.appendChild(div);
                });
                
                suggestionsDiv.style.display = 'block';
            });
    });
    
    document.addEventListener('click', (e) => {
        if (e.target !== patientInput && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.style.display = 'none';
        }
    });
}

function selectPatient(patient) {
    document.getElementById('selectedPatientId').value = patient.id;
    document.getElementById('patientName').value = patient.name;
    document.getElementById('patientCode').value = patient.patient_code || '';
    document.getElementById('patientCPF').value = patient.cpf;
    document.getElementById('patientBirthDate').value = patient.birth_date;
    document.getElementById('patientPhone').value = patient.phone;
    document.getElementById('patientAddress').value = patient.address;
    document.getElementById('patientCity').value = patient.city;
    document.getElementById('patientMotherName').value = patient.mother_name;
    document.getElementById('patientIndicationSource').value = patient.indication_source;
    document.getElementById('patientOccupation').value = patient.occupation;
    document.getElementById('patientType').value = patient.patient_type;
    document.getElementById('patientSuggestions').style.display = 'none';
}

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
        slot.style.cursor = 'pointer';
        slot.onclick = () => openNewAppointmentAtTime(hour);
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
        block.style.cursor = 'grab';
        block.draggable = true;
        block.dataset.appointmentId = app.id;
        block.dataset.duration = durationMinutes;
        
        // Evitar abrir detalhes ao arrastar
        let isDragging = false;
        block.addEventListener('mousedown', () => {
            isDragging = false;
        });
        block.addEventListener('mousemove', () => {
            isDragging = true;
        });
        block.addEventListener('click', (e) => {
            if (!isDragging) {
                selectAppointment(app);
            }
        });
        
        // Drag and drop events
        block.addEventListener('dragstart', (e) => {
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('appointmentId', app.id);
            e.dataTransfer.setData('duration', durationMinutes);
            block.style.opacity = '0.6';
        });
        
        block.addEventListener('dragend', () => {
            block.style.opacity = '1';
        });
        
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
    
    // Adicionar suporte para drop na grid
    appointmentsGrid.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    
    appointmentsGrid.addEventListener('drop', (e) => {
        e.preventDefault();
        const appointmentId = e.dataTransfer.getData('appointmentId');
        const duration = parseInt(e.dataTransfer.getData('duration'));
        
        // Calcular a nova hora baseada na posição do drop
        const grid = appointmentsGrid.getBoundingClientRect();
        const dropY = e.clientY - grid.top;
        
        // Cada hora tem 60px de altura (7am-7pm = 12 horas = 720px)
        const hourOffset = Math.round(dropY / 60);
        const newHour = 7 + Math.max(0, Math.min(12, hourOffset));
        const newMinutes = (dropY % 60 < 30) ? 0 : 30;
        
        // Criar nova data/hora
        const newStart = new Date(selectedDate);
        newStart.setHours(newHour, newMinutes, 0, 0);
        const newEnd = new Date(newStart.getTime() + duration * 60000);
        
        // Converter para string local
        function toLocalISOString(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
        }
        
        // Enviar atualização para o backend
        fetch(`/api/appointments/${appointmentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start: toLocalISOString(newStart),
                end: toLocalISOString(newEnd)
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                loadAppointments();
            } else {
                showAlert('Erro ao atualizar horário', 'danger');
            }
        })
        .catch(error => {
            showAlert('Erro ao arrastar agendamento', 'danger');
            console.error(error);
        });
    });
}

function getAppointmentTypeClass(type) {
    if (!type) return 'appointment-particular';
    if (type.includes('Transplante Capilar')) return 'appointment-transplante-capilar';
    if (type.includes('Botox') && type.includes('Retorno')) return 'appointment-retorno-botox';
    if (type.includes('Botox')) return 'appointment-botox';
    if (type.includes('Laser')) return 'appointment-laser';
    if (type.includes('Preenchimento')) return 'appointment-preenchimento';
    if (type.includes('Ulthera')) return 'appointment-ulthera';
    if (type.includes('Infiltração')) return 'appointment-infiltração-capilar';
    if (type.includes('Soroterapia')) return 'appointment-soroterapia';
    if (type.includes('Pequena Cirurgia')) return 'appointment-pequena-cirurgia';
    if (type.includes('Retirada')) return 'appointment-retirada-de-ponto';
    if (type.includes('Nitrogênio')) return 'appointment-nitrogênio-líquido';
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

function openNewAppointmentAtTime(hour) {
    clearAppointmentForm();
    
    const date = new Date(selectedDate);
    date.setHours(hour, 0, 0, 0);
    
    // Separar data e hora
    const dateStr = date.toISOString().split('T')[0];
    const timeStr = String(hour).padStart(2, '0') + ':00';
    
    document.getElementById('appointmentDate').value = dateStr;
    document.getElementById('appointmentTime').value = timeStr;
    document.getElementById('appointmentDuration').value = '30';
    
    const modal = new bootstrap.Modal(document.getElementById('newAppointmentModal'));
    modal.show();
    
    document.getElementById('patientName').focus();
}

function clearAppointmentForm() {
    const form = document.getElementById('appointmentForm');
    form.reset();
    document.getElementById('selectedPatientId').value = '';
    document.getElementById('patientCode').value = '';
    document.getElementById('patientSuggestions').style.display = 'none';
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
    
    // Converter para formato local sem timezone conversion
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
    // Pegar valores do formulário (datetime-local já está em formato local)
    const startStr = document.getElementById('editStartTime').value;
    const endStr = document.getElementById('editEndTime').value;
    
    // Adicionar :00 para segundos
    const payload = {
        patientName: document.getElementById('editPatientName').value,
        start: startStr + ':00',
        end: endStr + ':00',
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
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
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
    console.log('openPatientChart called');
    console.log('currentEvent:', currentEvent);
    console.log('patientId:', currentEvent?.extendedProps?.patientId);
    
    if (currentEvent && currentEvent.extendedProps.patientId) {
        const appointmentId = currentEvent.id;
        const patientId = currentEvent.extendedProps.patientId;
        
        // Fechar modal antes de redirecionar
        const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailModal'));
        if (modal) modal.hide();
        
        // Pequeno delay para permitir o modal fechar
        setTimeout(() => {
            window.location.href = `/prontuario/${patientId}?appointment_id=${appointmentId}`;
        }, 200);
    } else {
        console.error('Erro: currentEvent ou patientId não encontrado');
        alert('Erro: Não foi possível abrir o prontuário. Tente novamente.');
    }
}

function saveAppointment() {
    const patientName = document.getElementById('patientName').value.trim();
    const phone = document.getElementById('patientPhone').value;
    const cpf = document.getElementById('patientCPF').value;
    const birthDate = document.getElementById('patientBirthDate').value;
    const address = document.getElementById('patientAddress').value;
    const city = document.getElementById('patientCity').value;
    const motherName = document.getElementById('patientMotherName').value;
    const indicationSource = document.getElementById('patientIndicationSource').value;
    const occupation = document.getElementById('patientOccupation').value;
    const appointmentDate = document.getElementById('appointmentDate').value;
    const appointmentTime = document.getElementById('appointmentTime').value;
    const duration = parseInt(document.getElementById('appointmentDuration').value) || 30;
    const status = document.getElementById('appointmentStatus').value;
    const appointmentType = document.getElementById('appointmentType').value;
    const notes = document.getElementById('appointmentNotes').value;
    
    if (!patientName) {
        showAlert('Por favor, preencha o nome do paciente', 'warning');
        return;
    }
    
    if (!appointmentDate || !appointmentTime) {
        showAlert('Por favor, selecione data e hora do agendamento', 'warning');
        return;
    }
    
    let doctor_id = null;
    if (window.isSecretary) {
        doctor_id = document.getElementById('appointmentDoctor').value;
        if (!doctor_id) {
            showAlert('Por favor, selecione um médico', 'warning');
            return;
        }
    }
    
    // Combinar data e hora - manter como strings locais sem conversão de timezone
    const dateTimeStr = `${appointmentDate}T${appointmentTime}:00`;
    const startDate = new Date(dateTimeStr);
    if (isNaN(startDate.getTime())) {
        showAlert('Data/hora inválida. Por favor, tente novamente', 'danger');
        return;
    }
    
    // Calcular end date e converter para string local
    const endDate = new Date(startDate.getTime() + duration * 60000);
    
    // Converter para ISO string mantendo hora local
    function toLocalISOString(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
    }
    
    const payload = {
        patientName: patientName,
        phone: phone || null,
        cpf: cpf || null,
        birth_date: birthDate || null,
        address: address || null,
        city: city || null,
        mother_name: motherName || null,
        indication_source: indicationSource || null,
        occupation: occupation || null,
        start: toLocalISOString(startDate),
        end: toLocalISOString(endDate),
        status: status,
        appointmentType: appointmentType,
        notes: notes || null
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
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
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
