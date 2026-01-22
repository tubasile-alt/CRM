let appointmentsList = [];
let waitingRoomData = [];  // Armazena dados da sala de espera para atualização do timer

// Parsear string ISO como hora local (São Paulo) sem conversão de timezone
function parseLocalDateTime(isoString) {
    if (!isoString) return null;
    // Remove timezone designator usando regex (e.g., "+03:00" ou "-03:00")
    const cleanString = isoString.replace(/[+-]\d{2}:\d{2}$/, '').replace('Z', '');
    const [datePart, timePart] = cleanString.split('T');
    const [year, month, day] = datePart.split('-').map(Number);
    const timeParts = timePart ? timePart.split(':') : ['00', '00', '00'];
    const [hours, minutes, seconds] = timeParts.map(s => parseFloat(s));
    return new Date(year, month - 1, day, hours, Math.floor(minutes), Math.floor(seconds));
}

document.addEventListener('DOMContentLoaded', function() {
    // Para médicos, inicializar o filtro com seu próprio ID (se fornecido)
    if (window.isDoctor && window.currentDoctorId) {
        currentDoctorFilter = parseInt(window.currentDoctorId);
    }
    
    initializeDayView();
    initializeMonthCalendar();
    loadAppointments(); // renderDayView() será chamado dentro desta função após dados serem carregados
    updateWaitingCounter();
    setInterval(updateWaitingCounter, 30000);
    renderMiniCalendar();
    setupPatientAutocomplete();
    
    // Inicializar sala de espera
    startWaitingRoomUpdates();
});

function searchPatientsDetailed() {
    const query = document.getElementById('patientSearchInput').value.trim();
    if (query.length < 2) return;
    
    const resultsTable = document.getElementById('patientSearchResults');
    resultsTable.innerHTML = '<tr><td colspan="4" class="text-center"><div class="spinner-border spinner-border-sm"></div> Buscando...</td></tr>';
    
    fetch(`/api/patients/search_detailed?q=${encodeURIComponent(query)}`)
        .then(r => r.json())
        .then(patients => {
            resultsTable.innerHTML = '';
            if (patients.length === 0) {
                resultsTable.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Nenhum paciente encontrado</td></tr>';
                return;
            }
            
            patients.forEach(p => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${p.name}</td>
                    <td>${p.prontuario}</td>
                    <td>${p.last_consult}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="openPatientDetail(${p.id})">Acessar Ficha</button>
                    </td>
                `;
                resultsTable.appendChild(tr);
            });
        });
}

function openPatientDetail(patientId) {
    fetch(`/api/patient/${patientId}/history`)
        .then(r => r.json())
        .then(data => {
            const p = data.patient;
            document.getElementById('detailPatientId').value = p.id;
            document.getElementById('detailPatientName').value = p.name || '';
            document.getElementById('detailPatientCPF').value = p.cpf || '';
            document.getElementById('detailPatientPhone').value = p.phone || '';
            document.getElementById('detailPatientBirth').value = p.birth_date || '';
            document.getElementById('detailPatientAddress').value = p.address || '';
            
            const historyList = document.getElementById('patientHistoryList');
            historyList.innerHTML = '';
            
            if (data.history.length === 0) {
                historyList.innerHTML = '<div class="alert alert-light text-center">Nenhum histórico encontrado.</div>';
            } else {
                data.history.forEach(h => {
                    const card = document.createElement('div');
                    card.className = 'card mb-2 shadow-sm';
                    card.innerHTML = `
                        <div class="card-body p-2">
                            <div class="d-flex justify-content-between mb-1">
                                <strong class="small">${h.date} - ${h.category}</strong>
                                <span class="badge bg-light text-dark small">Dr. ${h.doctor}</span>
                            </div>
                            <div class="p-2 bg-light rounded small" style="white-space: pre-wrap; font-family: monospace;">${h.content || '(Sem conteúdo)'}</div>
                        </div>
                    `;
                    historyList.appendChild(card);
                });
            }
            
            // Fechar modal de busca e abrir ficha
            bootstrap.Modal.getOrCreateInstance(document.getElementById('searchPatientModal')).hide();
            new bootstrap.Modal(document.getElementById('patientDetailModal')).show();
        });
}

function savePatientChanges() {
    const id = document.getElementById('detailPatientId').value;
    const data = {
        name: document.getElementById('detailPatientName').value,
        cpf: document.getElementById('detailPatientCPF').value,
        phone: document.getElementById('detailPatientPhone').value,
        birth_date: document.getElementById('detailPatientBirth').value,
        address: document.getElementById('detailPatientAddress').value
    };
    
    fetch(`/api/patients/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            showAlert('Dados do paciente atualizados com sucesso!');
        } else {
            showAlert(res.error || 'Erro ao salvar alterações', 'danger');
        }
    });
}

    const patientInput = document.getElementById('patientName');
    const suggestionsDiv = document.getElementById('patientSuggestions');
    
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
        
        // Build URL - only include doctor_id if it has a value
        const url = doctorId 
            ? `/api/patients/search?q=${encodeURIComponent(query)}&doctor_id=${doctorId}`
            : `/api/patients/search?q=${encodeURIComponent(query)}`;
        
        fetch(url)
            .then(r => {
                if (!r.ok) {
                    throw new Error(`HTTP error! status: ${r.status}`);
                }
                return r.json();
            })
            .then(patients => {
                suggestionsDiv.innerHTML = '';
                if (!Array.isArray(patients) || patients.length === 0) {
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
            })
            .catch(err => {
                console.error('Erro ao buscar pacientes:', err);
                suggestionsDiv.style.display = 'none';
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
        for (let minutes = 0; minutes < 60; minutes += 15) {
            const slot = document.createElement('div');
            slot.className = 'hour-slot';
            slot.textContent = String(hour).padStart(2, '0') + ':' + String(minutes).padStart(2, '0');
            slot.style.cursor = 'pointer';
            slot.onclick = () => openNewAppointmentAtTime(hour, minutes);
            timeColumn.appendChild(slot);
        }
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
    
    console.log('Renderizando dia:', selectedDate.toDateString(), 'Total agendamentos:', appointmentsList.length, 'Filter:', currentDoctorFilter);
    
    const dayAppointments = appointmentsList.filter(app => {
        // Parse data sem timezone issues - pega apenas a parte da data (YYYY-MM-DD)
        const appDateStr = app.start.split('T')[0]; // "2025-11-27" da string ISO
        const selectedDateStr = selectedDate.getFullYear() + '-' + 
                               String(selectedDate.getMonth() + 1).padStart(2, '0') + '-' + 
                               String(selectedDate.getDate()).padStart(2, '0');
        const doctorMatch = !currentDoctorFilter || app.extendedProps?.doctorId == currentDoctorFilter;
        const dateMatch = appDateStr === selectedDateStr;
        const match = dateMatch && doctorMatch;
        if (!match) {
            console.log(`  Filtrado fora: ${app.title} | ${appDateStr} vs ${selectedDateStr} | doctorId: ${app.extendedProps?.doctorId} | dateMatch: ${dateMatch} | doctorMatch: ${doctorMatch}`);
        }
        return match;
    });
    
    console.log('Agendamentos após filtro:', dayAppointments.length);
    console.log('DEBUG - Primeiros 3 agendamentos:', dayAppointments.slice(0, 3).map(a => ({ title: a.title, start: a.start, id: a.id })));
    
    if (dayAppointments.length === 0) {
        appointmentsGrid.innerHTML = '<div class="empty-schedule">Nenhum agendamento para este dia</div>';
        return;
    }
    
    // Ordenar por horário
    dayAppointments.sort((a, b) => {
        const startA = parseLocalDateTime(a.start);
        const startB = parseLocalDateTime(b.start);
        return startA - startB;
    });
    
    dayAppointments.forEach(app => {
        const start = parseLocalDateTime(app.start);
        const end = parseLocalDateTime(app.end);
        const durationMinutes = (end - start) / (1000 * 60);
        
        // Formatar horário para exibição
        const timeStr = String(start.getHours()).padStart(2, '0') + ':' + String(start.getMinutes()).padStart(2, '0');
        
        // Extrair apenas o nome do paciente (sem nome do médico)
        const patientName = app.title ? app.title.split(' - ')[0] : 'Paciente';
        
        const appointmentType = app.extendedProps?.appointmentType || app.appointmentType || 'Particular';
        const patientType = app.extendedProps?.patientType || app.patientType || 'Particular';
        const patientCode = app.extendedProps?.patientCode || '-';
        const status = app.extendedProps?.status || app.status || 'agendado';
        const typeClass = getAppointmentTypeClass(appointmentType);
        const statusClass = `status-${status}`;
        
        const block = document.createElement('div');
        block.className = `appointment-block ${typeClass} ${statusClass}`;
        block.style.cursor = 'pointer';
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
        
        // Status icon
        let statusIcon = '🕐';
        if (status === 'confirmado') statusIcon = '✓';
        if (status === 'faltou') statusIcon = '✗';
        if (status === 'atendido') statusIcon = '✔';
        
        // Check if patient is waiting
        const isWaiting = app.extendedProps?.waiting || app.waiting || false;
        let actionBadgeHtml = '';
        
        if (status === 'atendido') {
            actionBadgeHtml = `<span class="atendido-badge"><i class="bi bi-check-circle-fill"></i> ATENDIDO</span>`;
        } else if (status === 'faltou') {
            actionBadgeHtml = `<span class="faltou-badge"><i class="bi bi-x-circle-fill"></i> FALTOU</span>`;
        } else if (isWaiting) {
            actionBadgeHtml = `<span class="waiting-badge"><i class="bi bi-hourglass-split"></i> Aguardando</span>`;
        } else {
            actionBadgeHtml = `<button class="checkin-btn" onclick="event.stopPropagation(); doCheckin(${app.id})" title="Fazer Check-in"><i class="bi bi-box-arrow-in-right"></i> Check In</button>`;
        }
        
        block.innerHTML = `
            <div class="appointment-content">
                <div class="appointment-info-line">
                    <span class="appointment-time-badge">${timeStr}</span>
                    <span class="appointment-name">${patientName}</span>
                    <span class="appointment-code">cod:${patientCode}</span>
                    <span class="appointment-type-label">pac:${patientType}</span>
                    <span class="appointment-consult-label">cons:${appointmentType}</span>
                    ${actionBadgeHtml}
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
        
        // Cada slot de 30min tem 30px de altura (7am-7pm = 24 slots = 720px)
        const slotOffset = Math.round(dropY / 30);
        const totalMinutes = 7 * 60 + slotOffset * 30;
        const newHour = Math.floor(totalMinutes / 60);
        const newMinutes = totalMinutes % 60;
        
        if (newHour < 7 || newHour > 19) return;
        
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

function openNewAppointmentAtTime(hour, minutes = 0) {
    clearAppointmentForm();
    
    const date = new Date(selectedDate);
    date.setHours(hour, minutes, 0, 0);
    
    // Separar data e hora
    const dateStr = date.toISOString().split('T')[0];
    const timeStr = String(hour).padStart(2, '0') + ':' + String(minutes).padStart(2, '0');
    
    document.getElementById('appointmentDate').value = dateStr;
    document.getElementById('appointmentTime').value = timeStr;
    document.getElementById('appointmentDuration').value = '15';
    
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
        start: parseLocalDateTime(app.start),
        end: parseLocalDateTime(app.end),
        extendedProps: app
    };
    
    // Secretária abre modal de edição, médico abre detalhes
    if (window.isSecretary) {
        openEditAppointmentModal(app);
    } else {
        showEventDetails(currentEvent);
    }
}

function openEditAppointmentModal(app) {
    document.getElementById('editAppointmentId').value = app.id;
    document.getElementById('editPatientName').value = app.patientName || '';
    document.getElementById('editPatientPhone').value = app.patientPhone || '';
    document.getElementById('editPatientType').value = app.patientType || 'Particular';
    document.getElementById('editAppointmentType').value = app.appointmentType || 'Particular';
    
    const start = parseLocalDateTime(app.start);
    const dateStr = start.toISOString().split('T')[0];
    const timeStr = String(start.getHours()).padStart(2, '0') + ':' + String(start.getMinutes()).padStart(2, '0');
    
    document.getElementById('editAppointmentDate').value = dateStr;
    document.getElementById('editAppointmentTime').value = timeStr;
    document.getElementById('editAppointmentDuration').value = Math.round((parseLocalDateTime(app.end) - start) / 60000);
    
    const modal = new bootstrap.Modal(document.getElementById('editAppointmentModal'));
    modal.show();
}

function deleteAppointment() {
    if (!confirm('Tem certeza que deseja deletar este agendamento?')) return;
    
    const appointmentId = document.getElementById('editAppointmentId').value;
    fetch(`/api/appointments/${appointmentId}`, {
        method: 'DELETE',
        headers: {'X-CSRFToken': getCSRFToken()}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('editAppointmentModal')).hide();
            loadAppointments();
        } else {
            alert(data.error || 'Erro ao deletar');
        }
    });
}

function updateAppointmentFromEdit() {
    const appointmentId = document.getElementById('editAppointmentId').value;
    const dateStr = document.getElementById('editAppointmentDate').value;
    const timeStr = document.getElementById('editAppointmentTime').value;
    const duration = parseInt(document.getElementById('editAppointmentDuration').value);
    
    // Validar se temos data e hora
    if (!dateStr || !timeStr) {
        showAlert('Data e hora são obrigatórias', 'danger');
        return;
    }

    const start = new Date(dateStr + 'T' + timeStr);
    const end = new Date(start.getTime() + duration * 60000);
    
    // Usar os mesmos nomes de campos que o backend espera no update_appointment
    const data = {
        patientName: document.getElementById('editPatientName').value,
        phone: document.getElementById('editPatientPhone').value,
        patientType: document.getElementById('editPatientType').value,
        appointmentType: document.getElementById('editAppointmentType').value,
        start: start.toISOString(),
        end: end.toISOString(),
        photo_data: document.getElementById('edit-patientPhotoData')?.value || '',
        // Incluir também versões com underscore para garantir
        patient_name: document.getElementById('editPatientName').value,
        patient_phone: document.getElementById('editPatientPhone').value,
        patient_type: document.getElementById('editPatientType').value,
        appointment_type: document.getElementById('editAppointmentType').value
    };
    
    console.log('[updateAppointmentFromEdit] Updating appointment:', appointmentId, data);
    
    fetch(`/api/appointments/${appointmentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(r => {
        if (!r.ok) throw new Error('Erro na rede');
        return r.json();
    })
    .then(data => {
        if (data.success) {
            showAlert('Agendamento atualizado com sucesso!');
            const modalEl = document.getElementById('editAppointmentModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            loadAppointments();
        } else {
            showAlert(data.error || 'Erro ao atualizar', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao atualizar agendamento', 'danger');
    });
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

// Photo handling
let webcamStream = null;

function setupWebcam(containerId, videoId, canvasId, previewId, placeholderId, startBtnId, captureBtnId, retakeBtnId, photoDataId) {
    const startBtn = document.getElementById(startBtnId);
    const captureBtn = document.getElementById(captureBtnId);
    const retakeBtn = document.getElementById(retakeBtnId);
    const video = document.getElementById(videoId);
    const canvas = document.getElementById(canvasId);
    const preview = document.getElementById(previewId);
    const placeholder = document.getElementById(placeholderId);
    const photoData = document.getElementById(photoDataId);

    startBtn.onclick = async () => {
        try {
            webcamStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            video.srcObject = webcamStream;
            video.style.display = 'block';
            placeholder.style.display = 'none';
            preview.style.display = 'none';
            startBtn.style.display = 'none';
            captureBtn.style.display = 'inline-block';
            retakeBtn.style.display = 'none';
        } catch (err) {
            console.error("Erro ao acessar webcam:", err);
            showAlert("Não foi possível acessar a webcam.", "danger");
        }
    };

    captureBtn.onclick = () => {
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const data = canvas.toDataURL('image/jpeg');
        photoData.value = data;
        
        preview.src = data;
        preview.style.display = 'block';
        video.style.display = 'none';
        captureBtn.style.display = 'none';
        retakeBtn.style.display = 'inline-block';
        
        if (webcamStream) {
            webcamStream.getTracks().forEach(track => track.stop());
        }
    };

    retakeBtn.onclick = () => {
        photoData.value = '';
        preview.style.display = 'none';
        placeholder.style.display = 'flex';
        startBtn.style.display = 'inline-block';
        retakeBtn.style.display = 'none';
    };
}

document.addEventListener('DOMContentLoaded', function() {
    // New Appointment Webcam
    setupWebcam(
        'webcam-container', 'webcam-video', 'photo-canvas', 'patient-photo-preview', 'webcam-placeholder',
        'start-webcam-btn', 'capture-photo-btn', 'retake-photo-btn', 'patientPhotoData'
    );
    
    // Edit Appointment Webcam
    setupWebcam(
        'edit-webcam-container', 'edit-webcam-video', 'edit-photo-canvas', 'edit-patient-photo-preview', 'edit-webcam-placeholder',
        'edit-start-webcam-btn', 'edit-capture-photo-btn', 'edit-retake-photo-btn', 'edit-patientPhotoData'
    );
    
    // Clean up webcam when modals close
    const newModal = document.getElementById('newAppointmentModal');
    const editModal = document.getElementById('editAppointmentModal');
    
    if (newModal) {
        newModal.addEventListener('hidden.bs.modal', function() {
            if (webcamStream) {
                webcamStream.getTracks().forEach(track => track.stop());
                webcamStream = null;
            }
            const video = document.getElementById('webcam-video');
            const placeholder = document.getElementById('webcam-placeholder');
            const preview = document.getElementById('patient-photo-preview');
            const startBtn = document.getElementById('start-webcam-btn');
            const captureBtn = document.getElementById('capture-photo-btn');
            const retakeBtn = document.getElementById('retake-photo-btn');
            const photoData = document.getElementById('patientPhotoData');
            
            if (video) video.style.display = 'none';
            if (placeholder) placeholder.style.display = 'flex';
            if (preview) preview.style.display = 'none';
            if (startBtn) startBtn.style.display = 'inline-block';
            if (captureBtn) captureBtn.style.display = 'none';
            if (retakeBtn) retakeBtn.style.display = 'none';
            if (photoData) photoData.value = '';
        });
    }
    
    if (editModal) {
        editModal.addEventListener('hidden.bs.modal', function() {
            if (webcamStream) {
                webcamStream.getTracks().forEach(track => track.stop());
                webcamStream = null;
            }
            const video = document.getElementById('edit-webcam-video');
            const placeholder = document.getElementById('edit-webcam-placeholder');
            const preview = document.getElementById('edit-patient-photo-preview');
            const startBtn = document.getElementById('edit-start-webcam-btn');
            const captureBtn = document.getElementById('edit-capture-photo-btn');
            const retakeBtn = document.getElementById('edit-retake-photo-btn');
            const photoData = document.getElementById('edit-patientPhotoData');
            
            if (video) video.style.display = 'none';
            if (placeholder) placeholder.style.display = 'flex';
            if (preview) preview.style.display = 'none';
            if (startBtn) startBtn.style.display = 'inline-block';
            if (captureBtn) captureBtn.style.display = 'none';
            if (retakeBtn) retakeBtn.style.display = 'none';
            if (photoData) photoData.value = '';
        });
    }
});

function loadAppointments() {
    let url = '/api/appointments';
    if (currentDoctorFilter) {
        url += `?doctor_id=${currentDoctorFilter}`;
    }
    
    fetch(url)
        .then(r => r.json())
        .then(events => {
            appointmentsList = events;
            console.log('=== Agendamentos carregados:', events.length, 'Total:', events);
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
    
    console.log('[saveAppointmentEdits] Saving changes for app:', currentEvent.id, payload);
    
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
    console.log('[updateEventStatus] Updating appointment', currentEvent.id, 'to status:', newStatus);
    
    fetch(`/api/appointments/${currentEvent.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: newStatus
        })
    })
    .then(response => {
        console.log('[updateEventStatus] Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('[updateEventStatus] Response data:', data);
        if (data.success) {
            showAlert('Status atualizado com sucesso!');
            console.log('[updateEventStatus] Success! Reloading appointments...');
            loadAppointments();
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('eventDetailModal')).hide();
            }, 500);
        } else {
            showAlert(data.error || 'Erro ao atualizar status', 'danger');
            console.error('[updateEventStatus] Server returned error:', data);
        }
    })
    .catch(error => {
        showAlert('Erro ao atualizar status.', 'danger');
        console.error('[updateEventStatus] Network error:', error);
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
    if (!currentEvent) {
        alert('Erro: Agendamento não encontrado. Tente novamente.');
        return;
    }
    
    // Acessar patientId (pode estar em diferentes níveis de aninhamento)
    let patientId = currentEvent.extendedProps?.patientId;
    
    // Se não encontrou, tenta no aninhamento duplo (há um bug na estrutura)
    if (!patientId && currentEvent.extendedProps?.extendedProps?.patientId) {
        patientId = currentEvent.extendedProps.extendedProps.patientId;
    }
    
    if (patientId) {
        const appointmentId = currentEvent.id;
        
        // Fechar modal antes de redirecionar
        const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailModal'));
        if (modal) modal.hide();
        
        // Pequeno delay para permitir o modal fechar
        setTimeout(() => {
            window.location.href = `/prontuario/${patientId}?appointment_id=${appointmentId}`;
        }, 200);
    } else {
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
    const surgeryName = document.getElementById('surgeryName')?.value?.trim() || '';
    
    if (!patientName) {
        showAlert('Por favor, preencha o nome do paciente', 'warning');
        return;
    }
    
    if (appointmentType === 'Cirurgia' && !surgeryName) {
        showAlert('Por favor, preencha o nome da cirurgia', 'warning');
        return;
    }
    
    if (!appointmentDate || !appointmentTime) {
        showAlert('Por favor, selecione data e hora do agendamento', 'warning');
        return;
    }
    
    let doctor_id = null;
    if (window.isSecretary) {
        doctor_id = parseInt(document.getElementById('appointmentDoctor').value);
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
    
    const photoDataEl = document.getElementById('patientPhotoData');
    const photoData = photoDataEl ? photoDataEl.value : null;
    
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
        notes: notes || null,
        surgery_name: surgeryName || null,
        photo_data: photoData || null
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
            let msg = 'Agendamento criado com sucesso!';
            if (data.surgery_created) {
                msg += ' Cirurgia adicionada ao Mapa Cirúrgico.';
            }
            showAlert(msg);
            loadAppointments();
            bootstrap.Modal.getInstance(document.getElementById('newAppointmentModal')).hide();
            document.getElementById('appointmentForm').reset();
            document.getElementById('surgeryNameRow').style.display = 'none';
            
            // Limpar dados da foto após salvar
            if (document.getElementById('patientPhotoData')) {
                document.getElementById('patientPhotoData').value = '';
            }
            if (document.getElementById('patient-photo-preview')) {
                document.getElementById('patient-photo-preview').style.display = 'none';
            }
            if (document.getElementById('webcam-placeholder')) {
                document.getElementById('webcam-placeholder').style.display = 'flex';
            }
            stopWebcam();
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

function toggleSurgeryNameField() {
    const patientType = document.getElementById('patientType').value;
    const surgeryNameRow = document.getElementById('surgeryNameRow');
    const surgeryNameInput = document.getElementById('surgeryName');
    
    if (patientType === 'cirurgia') {
        surgeryNameRow.style.display = 'block';
        surgeryNameInput.required = true;
    } else {
        surgeryNameRow.style.display = 'none';
        surgeryNameInput.required = false;
        surgeryNameInput.value = '';
    }
}

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// ==================== SALA DE ESPERA / CHECK-IN ====================

let waitingRoomInterval = null;

function doCheckin(appointmentId) {
    fetch(`/espera/api/checkin/${appointmentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showAlert('Check-in realizado! Paciente na sala de espera.');
            loadAppointments();
            loadWaitingRoom();
        } else {
            showAlert(data.error || 'Erro ao fazer check-in', 'danger');
        }
    })
    .catch(error => {
        showAlert('Erro ao fazer check-in', 'danger');
        console.error(error);
    });
}

function loadWaitingRoom() {
    const today = new Date().toISOString().split('T')[0];
    fetch(`/espera/api/list?date=${today}`, {
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        const waitingList = data.waiting_list || [];
        waitingRoomData = waitingList.map(patient => {
            let checkinTs = Date.now();
            if (patient.checked_in_time) {
                const parsed = new Date(patient.checked_in_time);
                if (!isNaN(parsed.getTime())) {
                    checkinTs = parsed.getTime();
                }
            }
            return {
                ...patient,
                checkinTimestamp: checkinTs
            };
        });
        renderWaitingRoom(waitingRoomData);
        const badge = document.getElementById('waitingCountBadge');
        if (badge) badge.textContent = waitingList.length;
    })
    .catch(error => {
        console.error('Erro ao carregar sala de espera:', error);
        const listDiv = document.getElementById('waitingRoomList');
        if (listDiv) listDiv.innerHTML = '<div class="waiting-empty">Erro ao carregar sala de espera</div>';
    });
}

function removeFromWaiting(appointmentId, event) {
    event.stopPropagation();
    event.preventDefault();
    if (!confirm('Remover paciente da lista de espera?')) return;
    
    fetch(`/espera/api/remove/${appointmentId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            loadWaitingRoom();
        } else {
            alert(data.error || 'Erro ao remover');
        }
    })
    .catch(e => {
        console.error('Erro ao remover da lista:', e);
        alert('Erro ao remover paciente da lista de espera');
    });
}

function renderWaitingRoom(waitingList) {
    const listDiv = document.getElementById('waitingRoomList');
    const badge = document.getElementById('waitingCountBadge');
    
    if (!listDiv) return;
    
    badge.textContent = waitingList.length;
    badge.style.display = waitingList.length > 0 ? 'inline-block' : 'none';
    
    if (waitingList.length === 0) {
        listDiv.innerHTML = '<div class="waiting-empty">Nenhum paciente aguardando</div>';
        return;
    }
    
    listDiv.innerHTML = waitingList.map(patient => {
        const waitMinutes = calculateMinutesSinceCheckin(patient.checkinTimestamp);
        const waitingTime = formatWaitingMinutes(waitMinutes);
        return `
            <div class="waiting-patient-item" data-patient-id="${patient.id}" onclick="openPatientFromWaiting(${patient.patient_id}, ${patient.id})">
                <div class="waiting-patient-info">
                    <span class="waiting-patient-name">${patient.patient_name}</span>
                    <span class="waiting-patient-type">${patient.appointment_type}</span>
                </div>
                <div class="waiting-timer" data-patient-id="${patient.id}">
                    <i class="bi bi-stopwatch"></i> ${waitingTime}
                </div>
                <button class="btn-remove-waiting" onclick="removeFromWaiting(${patient.id}, event)" title="Remover da lista de espera">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
        `;
    }).join('');
}

function formatWaitingMinutes(minutes) {
    if (minutes < 1) return '< 1 min';
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}min`;
}

function calculateMinutesSinceCheckin(checkinTimestamp) {
    if (!checkinTimestamp) return 0;
    const now = Date.now();
    const diffMs = now - checkinTimestamp;
    if (diffMs < 0) return 0;
    return Math.floor(diffMs / 60000);
}

function updateWaitingTimers() {
    if (!waitingRoomData || waitingRoomData.length === 0) return;
    
    const now = Date.now();
    waitingRoomData.forEach(patient => {
        const timer = document.querySelector(`.waiting-timer[data-patient-id="${patient.id}"]`);
        if (timer && patient.checkinTimestamp) {
            const diffMs = now - patient.checkinTimestamp;
            const minutes = diffMs > 0 ? Math.floor(diffMs / 60000) : 0;
            const seconds = diffMs > 0 ? Math.floor((diffMs % 60000) / 1000) : 0;
            
            // Mostrar minutos:segundos para precisão
            let timeText;
            if (minutes < 1) {
                timeText = `${seconds}s`;
            } else if (minutes < 60) {
                timeText = `${minutes}m ${seconds}s`;
            } else {
                const hours = Math.floor(minutes / 60);
                const mins = minutes % 60;
                timeText = `${hours}h ${mins}m`;
            }
            timer.innerHTML = `<i class="bi bi-stopwatch"></i> ${timeText}`;
        }
    });
}

function openPatientFromWaiting(patientId, appointmentId) {
    window.location.href = `/prontuario/${patientId}?appointment_id=${appointmentId}`;
}

function startWaitingRoomUpdates() {
    loadWaitingRoom();
    if (waitingRoomInterval) clearInterval(waitingRoomInterval);
    
    // Atualizar timers a cada 1 segundo
    waitingRoomInterval = setInterval(updateWaitingTimers, 1000);
    
    // Recarregar lista a cada 30 segundos (não a cada 5 para não interferir com o timer)
    setInterval(loadWaitingRoom, 30000);
    
    // Primeira atualização imediata após 100ms
    setTimeout(updateWaitingTimers, 100);
}

// Page unload cleanup for webcam streams
window.addEventListener('beforeunload', function() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
    }
});
