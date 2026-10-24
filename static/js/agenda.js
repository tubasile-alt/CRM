(function() {
    let appointmentsList = [];
    const APPOINTMENT_TYPES = [
        'Particular',
        'Patologia',
        'Botox',
        'Retorno Botox',
        'Laser',
        'Preenchimento',
        'Retorno Preenchimento',
        'Sculptra',
        'Ulthera',
        'Retorno Ulthera',
        'Morpheus',
        'Retorno Morpheus',
        'Implante Capilar',
        '1º Implante Capilar',
        'Retorno Implante Capilar',
        'Infiltração Capilar',
        'Soroterapia',
        'Pequena Cirurgia',
        'Retirada de Ponto',
        'Nitrogênio Líquido',
        'Transplante Capilar',
        'Retorno 1 semana TX',
        'Retorno Transplante',
        'Retorno',
        'UNIMED',
        'Cortesia'
    ];
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
        _setupDragToReschedule();

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
                        const contactInfo = [item.patient_phone, item.patient_cpf ? `CPF ${item.patient_cpf}` : ''].filter(Boolean).join(' · ');
                        div.innerHTML = `<span class="fw-semibold">${item.patient_name}</span> <span class="text-muted small">— Dr(a). ${item.doctor_name} (${roleLabel}) — Cód. ${item.patient_code || '-'}</span>${contactInfo ? `<div class="text-muted small">${contactInfo}</div>` : ''}`;
                        div.onclick = () => selectPatient({
                            id: item.patient_id,
                            name: item.patient_name,
                            dp_id: item.dp_id,
                            patient_code: item.patient_code,
                            phone: item.patient_phone,
                            cpf: item.patient_cpf,
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
                <button onclick="previousMonth()" aria-label="Mês anterior"><i class="bi bi-chevron-left"></i></button>
                <div class="mini-calendar-title">
                    ${new Date(currentYear, currentMonth).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
                </div>
                <button onclick="nextMonth()" aria-label="Próximo mês"><i class="bi bi-chevron-right"></i></button>
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

    function normalizeAppointmentType(value) {
        return String(value || '')
            .trim()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    }

    function getAppointmentTypeClass(type, patientType) {
        const normalizedType = normalizeAppointmentType(type || 'Particular');
        const normalizedPatientType = normalizeAppointmentType(patientType);

        if (normalizedType === 'particular' && normalizedPatientType === 'unimed') {
            return 'appointment-unimed';
        }
        if (normalizedType.includes('pequena cirurgia')) return 'appointment-pequena-cirurgia';
        if (normalizedType === 'cirurgia') return 'appointment-cirurgia';
        if (normalizedType.includes('unimed')) return 'appointment-unimed';
        if (normalizedType.includes('cortesia')) return 'appointment-cortesia';
        if (normalizedType.includes('transplante') || /\btx\b/.test(normalizedType)) return 'appointment-transplante';
        if (normalizedType.includes('preenchimento')) return 'appointment-preenchimento';
        if (normalizedType.includes('botox')) return 'appointment-botox';
        if (normalizedType.includes('laser')) return 'appointment-laser';
        if (normalizedType.includes('sculptra')) return 'appointment-sculptra';
        if (normalizedType.includes('ulthera')) return 'appointment-ulthera';
        if (normalizedType.includes('morpheus')) return 'appointment-morpheus';
        if (normalizedType.includes('infiltracao capilar')) return 'appointment-infiltracao-capilar';
        if (normalizedType.includes('soroterapia')) return 'appointment-soroterapia';
        if (normalizedType.includes('retirada de ponto')) return 'appointment-retirada-de-ponto';
        if (normalizedType.includes('nitrogenio liquido')) return 'appointment-nitrogenio-liquido';
        if (normalizedType.includes('patologia')) return 'appointment-patologia';
        if (normalizedType.includes('implante capilar')) return 'appointment-implante-capilar';
        if (normalizedType.includes('retorno')) return 'appointment-retorno';
        return 'appointment-particular';
    }

    // Cor da barra lateral de cada linha, por tipo de consulta
    const TYPE_COLORS = {
        'appointment-particular': '#ffc107',
        'appointment-patologia': '#287f8c',
        'appointment-botox': '#6f42c1',
        'appointment-laser': '#fd7e14',
        'appointment-preenchimento': '#e83e8c',
        'appointment-sculptra': '#d85b32',
        'appointment-ulthera': '#0056b3',
        'appointment-morpheus': '#5146a5',
        'appointment-infiltracao-capilar': '#28a745',
        'appointment-soroterapia': '#17a2b8',
        'appointment-pequena-cirurgia': '#c2185b',
        'appointment-retirada-de-ponto': '#7b1fa2',
        'appointment-nitrogenio-liquido': '#0097a7',
        'appointment-transplante': '#dc3545',
        'appointment-implante-capilar': '#17a2b8',
        'appointment-retorno': '#0098d9',
        'appointment-unimed': '#198754',
        'appointment-cortesia': '#6c757d',
        'appointment-cirurgia': '#ff3b30'
    };

    // Grade da secretária: 07:00–20:00 em intervalos de 15 min (mesma grade da agenda antiga)
    const DAY_START_MIN = 7 * 60;
    const DAY_END_MIN = 20 * 60;
    const SLOT_MIN = 15;

    function pad2(n) { return String(n).padStart(2, '0'); }
    function minutesToHHMM(m) { return `${pad2(Math.floor(m / 60))}:${pad2(m % 60)}`; }
    function minutesOfDay(date) { return date.getHours() * 60 + date.getMinutes(); }
    function toLocalISO(date) {
        return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}T${pad2(date.getHours())}:${pad2(date.getMinutes())}:00`;
    }
    function escapeHtml(value) {
        return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    }

    function appInfo(app) {
        const props = app.extendedProps || {};
        const start = parseLocalDateTime(app.start);
        const end = parseLocalDateTime(app.end);
        // actualDuration é a duração gravada (preservada ao remarcar); duration tem no mínimo um slot,
        // para exibição e para marcar os horários ocupados
        const actualDuration = end && start && end > start ? Math.round((end - start) / 60000) : SLOT_MIN;
        const duration = Math.max(SLOT_MIN, actualDuration);
        const status = props.status || app.status || 'agendado';
        const isSurgeryMap = !!props.isSurgeryMap;
        const typeClass = isSurgeryMap ? 'appointment-cirurgia'
            : getAppointmentTypeClass(props.appointmentType || app.appointmentType, props.patientType || app.patientType);
        return {
            start, end, duration, actualDuration, status, isSurgeryMap, typeClass,
            startMin: start ? minutesOfDay(start) : 0,
            patientName: app.title ? app.title.split(' - ')[0] : 'Paciente',
            appointmentType: props.appointmentType || app.appointmentType || 'Particular',
            patientType: props.patientType || app.patientType || 'Particular',
            patientCode: props.patientCode ?? null,
            patientId: props.patientId || app.patientId,
            doctorId: props.doctorId || app.doctorId,
            doctorName: props.doctorName || '',
            isProvisorio: (props.statusCadastral || 'ativo') === 'provisorio',
            isWaiting: !!(props.waiting || app.waiting),
            checkedInTime: props.checkedInTime || null,
            ivpStars: props.ivpStars,
            isDone: status === 'atendido' || status === 'faltou'
        };
    }

    function canReschedule(app, info) {
        return !!window.isSecretary && /^\d+$/.test(String(app.id)) && !info.isSurgeryMap && !info.isDone && !info.isWaiting;
    }

    function _buildActions(app, info) {
        const id = app.id;
        let html = '';
        if (info.isProvisorio) {
            html = `<button class="ag-pill ag-pill-orange-soft" onclick="event.stopPropagation(); openEditAppointmentModalById('${id}')"
                    title="Editar cadastro provisório"><i class="bi bi-pencil-square"></i> Editar cadastro</button>`;
        } else if (info.status === 'atendido') {
            html = `<span class="ag-pill ag-pill-green-soft"><i class="bi bi-check-circle-fill"></i> Atendido</span>`;
        } else if (info.status === 'faltou') {
            html = `<span class="ag-pill ag-pill-red-soft"><i class="bi bi-x-circle-fill"></i> Faltou</span>
                    <button class="ag-pill ag-pill-neutral" onclick="event.stopPropagation(); doCheckin('${id}')" title="Chegou atrasado - Fazer Check-in"><i class="bi bi-box-arrow-in-right"></i> Check In</button>`;
        } else if (info.isWaiting) {
            html = `<span class="ag-pill ag-pill-yellow-soft"><i class="bi bi-hourglass-split"></i> Na espera</span>
                    <button class="ag-pill ag-pill-blue" onclick="event.stopPropagation(); doCheckout('${id}')" title="Finalizar atendimento"><i class="bi bi-check2-circle"></i> Finalizar</button>
                    <button class="ag-pill ag-pill-ghost" onclick="event.stopPropagation(); removeFromWaiting('${id}')" title="Remover da espera (sem finalizar)" aria-label="Remover da espera"><i class="bi bi-x-lg"></i></button>`;
        } else if (!info.isSurgeryMap) {
            html = `<button class="ag-pill ag-pill-green" onclick="event.stopPropagation(); doCheckin('${id}')" title="Fazer Check-in"><i class="bi bi-box-arrow-in-right"></i> Check In</button>`;
        }

        if (info.isProvisorio && (window.isSecretary || window.isDoctor)) {
            const props = app.extendedProps || {};
            const q = v => String(v || '').replace(/'/g, "\\'");
            html += `<button class="ag-pill ag-pill-orange"
                    onclick="event.stopPropagation(); abrirModalAtivacao(${info.patientId}, '${q(info.patientName)}', ${info.doctorId || 'null'}, '${q(props.phone)}', '${q(props.cpf)}')"
                    title="Ativar cadastro deste paciente"><i class="bi bi-person-check"></i> Ativar</button>`;
        }
        if (info.isSurgeryMap && info.patientId) {
            html += `<button class="ag-pill ag-pill-neutral" onclick="event.stopPropagation(); goToPatientChart(${info.patientId}, '${id}')" title="Ver prontuário"><i class="bi bi-file-medical"></i> Prontuário</button>`;
        }
        return html;
    }

    function _buildAppointmentBlock(app) {
        const info = appInfo(app);
        const timeStr = info.start ? minutesToHHMM(info.startMin) : '--:--';
        const draggable = canReschedule(app, info);

        const row = document.createElement('div');
        row.className = 'ag-row'
            + (info.isDone ? ' is-done' : '')
            + (info.status === 'faltou' ? ' is-missed' : '')
            + (info.isProvisorio ? ' is-provisorio' : '')
            + (info.isWaiting ? ' is-waiting' : '')
            + (info.isSurgeryMap ? ' is-surgery' : '');
        row.style.setProperty('--bar', TYPE_COLORS[info.typeClass] || '#ffc107');
        row.dataset.appointmentId = app.id;
        row.dataset.slot = timeStr;
        row.dataset.min = info.startMin;

        const stars = info.ivpStars ? `<span class="ag-stars">${'⭐'.repeat(info.ivpStars)}</span>` : '';
        const meta = [escapeHtml(info.appointmentType)];
        if (window.isSecretary) {
            if (!info.isProvisorio) meta.push(`cód ${info.patientCode !== null ? escapeHtml(info.patientCode) : '-'}`);
            meta.push(escapeHtml(info.patientType));
            if (!currentDoctorFilter && info.doctorName) meta.push(escapeHtml(info.doctorName));
        }
        const tags = (info.isProvisorio ? '<span class="ag-tag ag-tag-orange">Provisório</span>' : '')
            + (info.isSurgeryMap ? '<span class="ag-tag ag-tag-red">Cirurgia</span>' : '');
        const grip = draggable
            ? `<button type="button" class="ag-grip" aria-label="Arrastar para remarcar" title="Arraste para remarcar"><i class="bi bi-grip-vertical"></i></button>`
            : (window.isSecretary ? '<span class="ag-grip-space"></span>' : '');
        const duration = info.duration > SLOT_MIN ? `<small>${info.duration} min</small>` : '';
        const nameClick = `event.stopPropagation(); if(${info.patientId || 0} && !${info.isProvisorio}) { goToPatientChart(${info.patientId || 0}, '${app.id}') } else if(${info.isProvisorio}) { showAlert('Cadastro provisório — ative primeiro para acessar o prontuário.', 'warning') } else { showAlert('Paciente não vinculado ao prontuário', 'warning') }`;

        row.innerHTML = `
            ${grip}
            <span class="ag-time">${timeStr}${duration}</span>
            <div class="ag-main">
                <span class="ag-name" onclick="${nameClick}">${escapeHtml(info.patientName)}${stars}</span>${tags}
                <span class="ag-meta">${meta.join(' · ')}</span>
            </div>
            <div class="ag-actions">${_buildActions(app, info)}</div>`;

        row.onclick = () => selectAppointment(app);
        return row;
    }

    function _buildFreeSlot(min) {
        const row = document.createElement('div');
        row.className = 'ag-slot';
        row.dataset.slot = minutesToHHMM(min);
        row.dataset.min = min;
        row.innerHTML = `<span class="ag-grip-space"></span><span class="ag-time">${minutesToHHMM(min)}</span>
            <span class="ag-slot-line"></span><span class="ag-slot-add"><i class="bi bi-plus-lg"></i> Agendar</span>`;
        row.onclick = () => window.openNewAppointmentAtTime(Math.floor(min / 60), min % 60);
        return row;
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

    function getDayAppointments() {
        const selectedDateStr = selectedDate.toDateString();
        return appointmentsList.filter(app => {
            const start = parseLocalDateTime(app.start);
            if (!start || start.toDateString() !== selectedDateStr) return false;
            const doctorId = parseInt(app.extendedProps?.doctorId || app.doctorId || app.doctor_id);
            return !currentDoctorFilter || doctorId === currentDoctorFilter;
        }).sort((a, b) => parseLocalDateTime(a.start) - parseLocalDateTime(b.start));
    }

    function isSelectedDateToday() {
        return selectedDate.toDateString() === todayISO_BR().toDateString();
    }

    // Linhas do dia, em ordem. Médico: só consultas. Secretária: grade de 15 min com os horários
    // livres; consultas simultâneas aparecem todas no mesmo horário e as fora de 07:00–20:00
    // vêm antes/depois da grade (nunca somem).
    function buildDayRows(dayAppointments, withFreeSlots) {
        const infos = dayAppointments
            .map(app => ({ app, info: appInfo(app) }))
            .filter(({ info }) => info.start)
            .sort((x, y) => x.info.start - y.info.start);
        if (!withFreeSlots) return infos.map(({ app }) => ({ type: 'appointment', app }));

        // Horários dentro de uma consulta (mínimo de 15 min) não aparecem como livres
        const covered = new Set();
        infos.forEach(({ info }) => {
            const firstSlot = Math.floor(info.startMin / SLOT_MIN) * SLOT_MIN;
            for (let m = firstSlot; m < info.startMin + info.duration; m += SLOT_MIN) {
                covered.add(m);
            }
        });
        const rows = [];
        const pushApps = list => list.forEach(({ app }) => rows.push({ type: 'appointment', app }));
        pushApps(infos.filter(({ info }) => info.startMin < DAY_START_MIN));
        for (let min = DAY_START_MIN; min < DAY_END_MIN; min += SLOT_MIN) {
            const here = infos.filter(({ info }) => info.startMin >= min && info.startMin < min + SLOT_MIN);
            if (here.length) pushApps(here);
            else if (!covered.has(min)) rows.push({ type: 'free', min });
        }
        pushApps(infos.filter(({ info }) => info.startMin >= DAY_END_MIN));
        return rows;
    }

    window.__agendaDayLayout = { buildDayRows, appInfo };

    function _renderRows(grid, dayAppointments) {
        const rows = buildDayRows(dayAppointments, !!window.isSecretary);
        rows.forEach(row => grid.appendChild(
            row.type === 'free' ? _buildFreeSlot(row.min) : _buildAppointmentBlock(row.app)
        ));
        return rows.filter(row => row.type === 'free').length;
    }

    function _insertNowLine(grid) {
        if (!isSelectedDateToday()) return;
        const nowMin = minutesOfDay(todayISO_BR());
        const rows = [...grid.querySelectorAll('[data-min]')];
        if (!rows.length) return;
        const line = document.createElement('div');
        line.className = 'ag-now';
        line.innerHTML = `<span>${minutesToHHMM(nowMin)}</span>`;
        const next = rows.find(r => parseInt(r.dataset.min) > nowMin);
        if (next) grid.insertBefore(line, next);
        else grid.appendChild(line);
    }

    function _renderNextCard(dayAppointments) {
        const card = document.getElementById('agNextCard');
        if (!card) return;
        card.innerHTML = '';
        if (window.isSecretary || !isSelectedDateToday()) return;

        const nowMin = minutesOfDay(todayISO_BR());
        const infos = dayAppointments.map(app => ({ app, info: appInfo(app) }))
            .filter(({ info }) => !info.isDone && !info.isSurgeryMap);
        const waiting = infos.find(({ info }) => info.isWaiting);
        const upcoming = infos.find(({ info }) => info.startMin >= nowMin - 10);
        const pick = waiting || upcoming;
        if (!pick) return;

        const { app, info } = pick;
        let eyebrow;
        if (info.isWaiting) {
            const since = info.checkedInTime ? minutesSince(info.checkedInTime) : null;
            eyebrow = since !== null ? `Na sala de espera · há ${since} min` : 'Na sala de espera';
        } else {
            const diff = info.startMin - nowMin;
            eyebrow = diff > 0 ? `Próximo paciente · em ${diff} min` : 'Próximo paciente · agora';
        }
        const meta = [minutesToHHMM(info.startMin), escapeHtml(info.appointmentType)];
        if (info.patientCode !== null) meta.push(`Cód. ${escapeHtml(info.patientCode)}`);
        meta.push(escapeHtml(info.patientType));

        const canOpenChart = info.patientId && !info.isProvisorio;
        card.innerHTML = `
            <section class="ag-next" aria-label="Próximo paciente">
                <div>
                    <div class="ag-eyebrow">${eyebrow}</div>
                    <div class="ag-next-name">${escapeHtml(info.patientName)}</div>
                    <div class="ag-next-meta">${meta.join(' · ')}</div>
                </div>
                <div class="ag-next-actions">
                    <button type="button" class="ag-capsule" data-act="details">Detalhes</button>
                    ${canOpenChart ? `<button type="button" class="ag-capsule ag-primary" data-act="chart"><i class="bi bi-file-medical"></i> Abrir prontuário</button>` : ''}
                </div>
            </section>`;
        card.querySelector('[data-act="details"]').onclick = () => selectAppointment(app);
        const chartBtn = card.querySelector('[data-act="chart"]');
        if (chartBtn) chartBtn.onclick = () => goToPatientChart(info.patientId, app.id);
    }

    function _renderDayStats(dayAppointments, freeCount) {
        const infos = dayAppointments.map(appInfo);
        const total = infos.length;
        const done = infos.filter(i => i.status === 'atendido').length;
        const missed = infos.filter(i => i.status === 'faltou').length;
        const stats = window.isSecretary
            ? [['Agendados', total], ['Horários livres', freeCount], ['Atendidos', done]]
            : [['Atendidos', `${done} de ${total}`], ['Faltas', missed]];
        const el = document.getElementById('agDayStats');
        if (el) el.innerHTML = stats.map(([l, v]) => `<div class="ag-side-row"><span>${l}</span><b>${v}</b></div>`).join('');

        const sub = document.getElementById('agSubtitle');
        if (sub) {
            const parts = [`${total} ${total === 1 ? 'consulta' : 'consultas'}`];
            if (window.isSecretary) {
                parts.push(`${freeCount} ${freeCount === 1 ? 'horário livre' : 'horários livres'}`);
                const activeBtn = document.querySelector('.doctor-filter-btns .btn.active');
                parts.push(currentDoctorFilter && activeBtn ? activeBtn.textContent.trim() : 'todos os médicos');
            }
            sub.textContent = parts.join(' · ');
        }
    }

    window.renderDayView = function() {
        const appointmentsGrid = document.getElementById('appointmentsGrid');
        if (!appointmentsGrid) return;
        appointmentsGrid.innerHTML = '';
        updateProvisorioBadge();

        // Animar a entrada só quando o dia/filtro muda, não no auto-refresh
        const renderKey = selectedDate.toDateString() + '|' + (currentDoctorFilter || 'all');
        appointmentsGrid.classList.toggle('aa-animate', appointmentsGrid.dataset.renderKey !== renderKey);
        appointmentsGrid.dataset.renderKey = renderKey;

        const dayAppointments = getDayAppointments();
        const freeCount = _renderRows(appointmentsGrid, dayAppointments);
        _renderNextCard(dayAppointments);
        _renderDayStats(dayAppointments, freeCount);

        if (!window.isSecretary && dayAppointments.length === 0) {
            appointmentsGrid.innerHTML = '<div class="ag-empty"><i class="bi bi-calendar2-check"></i>Nenhum paciente marcado para este dia</div>';
            return;
        }
        _insertNowLine(appointmentsGrid);
    };

    // ==================== ARRASTAR PARA REMARCAR (secretária) ====================
    let dragState = null;
    const DRAG_THRESHOLD = 6;
    const EDGE_SCROLL_ZONE = 80;

    function _setupDragToReschedule() {
        const grid = document.getElementById('appointmentsGrid');
        if (!grid || !window.isSecretary) return;

        grid.addEventListener('pointerdown', e => {
            const grip = e.target.closest('.ag-grip');
            if (!grip || e.button !== 0 || dragState) return;
            const row = grip.closest('.ag-row');
            const app = appointmentsList.find(a => String(a.id) === row.dataset.appointmentId);
            if (!app) return;
            e.preventDefault();
            grip.setPointerCapture(e.pointerId);
            dragState = { app, row, grip, pointerId: e.pointerId, startX: e.clientX, startY: e.clientY, x: e.clientX, y: e.clientY, started: false, target: null };
        });
        // O clique na alça não abre o modal da linha
        grid.addEventListener('click', e => { if (e.target.closest('.ag-grip')) e.stopPropagation(); }, true);
        // Teclado: Enter/Espaço na alça abre a edição, onde também se troca o horário
        grid.addEventListener('keydown', e => {
            const grip = e.target.closest('.ag-grip');
            if (!grip || (e.key !== 'Enter' && e.key !== ' ')) return;
            e.preventDefault();
            const app = appointmentsList.find(a => String(a.id) === grip.closest('.ag-row').dataset.appointmentId);
            if (app) selectAppointment(app);
        });

        document.addEventListener('pointermove', e => {
            if (!dragState || e.pointerId !== dragState.pointerId) return;
            dragState.x = e.clientX;
            dragState.y = e.clientY;
            if (!dragState.started) {
                if (Math.hypot(e.clientX - dragState.startX, e.clientY - dragState.startY) < DRAG_THRESHOLD) return;
                _startDrag();
            }
            _updateDrag();
        });
        document.addEventListener('pointerup', e => {
            if (!dragState || e.pointerId !== dragState.pointerId) return;
            if (!dragState.started) { dragState = null; return; }
            const target = dragState.target;
            if (target && target.dataset.slot !== dragState.row.dataset.slot) _commitDrag(target);
            else _cancelDrag();
        });
        document.addEventListener('pointercancel', e => {
            if (dragState && e.pointerId === dragState.pointerId) _cancelDrag();
        });
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape' && dragState && dragState.started) _cancelDrag();
        });
    }

    function _startDrag() {
        const { row } = dragState;
        const rect = row.getBoundingClientRect();
        const floating = row.cloneNode(true);
        floating.classList.add('ag-floating');
        floating.removeAttribute('data-slot');
        floating.removeAttribute('data-min');
        floating.style.left = `${rect.left}px`;
        floating.style.top = `${rect.top}px`;
        floating.style.width = `${rect.width}px`;
        document.body.appendChild(floating);
        row.classList.add('is-drag-origin');
        document.body.classList.add('ag-dragging');
        Object.assign(dragState, { started: true, floating, rect });
        _autoScrollLoop();
    }

    function _updateDrag() {
        const s = dragState;
        s.floating.style.transform = `translate(${s.x - s.startX}px, ${s.y - s.startY}px) scale(1.02)`;

        const under = document.elementFromPoint(s.x, s.y);
        const target = under ? under.closest('#appointmentsGrid [data-slot]') : null;
        if (target !== s.target) {
            if (s.target) s.target.classList.remove('is-drop-target');
            s.target = target && target !== s.row ? target : null;
            if (s.target) s.target.classList.add('is-drop-target');
        }
        const name = appInfo(s.app).patientName;
        const to = s.target ? s.target.dataset.slot : null;
        const timeEl = s.floating.querySelector('.ag-time');
        if (timeEl) timeEl.firstChild.textContent = to || s.row.dataset.slot;
        const fit = s.target && s.target.classList.contains('ag-row') ? ' (encaixe)' : '';
        _showToast(to
            ? `<i class="bi bi-arrows-move"></i> Remarcar <b>${escapeHtml(name)}</b> de ${s.row.dataset.slot} para <b>${to}</b>${fit} <kbd>Esc</kbd> cancela`
            : `<i class="bi bi-arrows-move"></i> Arraste <b>${escapeHtml(name)}</b> até um horário <kbd>Esc</kbd> cancela`);
    }

    function _autoScrollLoop() {
        if (!dragState || !dragState.started) return;
        const y = dragState.y;
        let speed = 0;
        if (y < EDGE_SCROLL_ZONE) speed = -Math.ceil((EDGE_SCROLL_ZONE - y) / 6);
        else if (y > window.innerHeight - EDGE_SCROLL_ZONE) speed = Math.ceil((y - (window.innerHeight - EDGE_SCROLL_ZONE)) / 6);
        if (speed) {
            // 'instant': o Bootstrap liga scroll-behavior: smooth no <html>, o que atrasaria o arraste
            window.scrollBy({ top: speed, behavior: 'instant' });
            _updateDrag();
        }
        requestAnimationFrame(_autoScrollLoop);
    }

    function _endDrag() {
        const s = dragState;
        dragState = null;
        if (!s) return;
        if (s.target) s.target.classList.remove('is-drop-target');
        s.row.classList.remove('is-drag-origin');
        document.body.classList.remove('ag-dragging');
        try { s.grip.releasePointerCapture(s.pointerId); } catch (_) { /* já liberado */ }
        return s;
    }

    function _animateFloatingTo(floating, dx, dy, done) {
        const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduce) { floating.remove(); done && done(); return; }
        floating.classList.add('is-settling');
        floating.style.transform = `translate(${dx}px, ${dy}px) scale(1)`;
        let finished = false;
        const finish = () => { if (finished) return; finished = true; floating.remove(); done && done(); };
        floating.addEventListener('transitionend', finish, { once: true });
        setTimeout(finish, 320);
    }

    function _cancelDrag() {
        const s = _endDrag();
        if (!s) return;
        _hideToast();
        // Volta pelo mesmo caminho até a posição de origem
        const r = s.row.getBoundingClientRect();
        _animateFloatingTo(s.floating, r.left - s.rect.left, r.top - s.rect.top);
    }

    function _commitDrag(target) {
        const s = _endDrag();
        const { app } = s;
        const r = target.getBoundingClientRect();
        _animateFloatingTo(s.floating, r.left - s.rect.left, r.top - s.rect.top, () => {
            const [h, m] = target.dataset.slot.split(':').map(Number);
            const info = appInfo(app);
            const newStart = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), selectedDate.getDate(), h, m);
            const newEnd = new Date(newStart.getTime() + info.actualDuration * 60000);
            _rescheduleAppointment(app, toLocalISO(newStart), toLocalISO(newEnd), { undoable: true });
        });
    }

    function _rescheduleAppointment(app, start, end, { undoable }) {
        const previous = { start: app.start, end: app.end };
        const name = appInfo(app).patientName;
        app.start = start;
        app.end = end;
        renderDayView();

        fetch(`/api/appointments/${app.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ start, end })
        })
        .then(r => r.json())
        .then(data => {
            if (!data.success) throw new Error(data.error || 'Erro ao remarcar');
            if (calendar) calendar.refetchEvents();
            const hhmm = start.slice(11, 16);
            if (undoable) {
                _showToast(`<i class="bi bi-check-circle-fill"></i> <b>${escapeHtml(name)}</b> remarcado para <b>${hhmm}</b>`, {
                    timeout: 8000,
                    action: { label: 'Desfazer', run: () => _rescheduleAppointment(app, previous.start, previous.end, { undoable: false }) }
                });
            } else {
                _showToast(`<i class="bi bi-arrow-counterclockwise"></i> Remarcação desfeita`, { timeout: 3000 });
            }
        })
        .catch(err => {
            console.error(err);
            app.start = previous.start;
            app.end = previous.end;
            renderDayView();
            _hideToast();
            showAlert(err.message || 'Erro ao remarcar', 'danger');
        });
    }

    let _toastTimer = null;
    function _showToast(html, { timeout = 0, action = null } = {}) {
        const toast = document.getElementById('agToast');
        if (!toast) return;
        clearTimeout(_toastTimer);
        toast.innerHTML = `<span>${html}</span>`;
        if (action) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = action.label;
            btn.onclick = () => { _hideToast(); action.run(); };
            toast.appendChild(btn);
        }
        toast.hidden = false;
        if (timeout) _toastTimer = setTimeout(_hideToast, timeout);
    }

    function _hideToast() {
        const toast = document.getElementById('agToast');
        if (toast) toast.hidden = true;
        clearTimeout(_toastTimer);
    }

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

    function _autoRefreshAppointments() {
        if (_isAnyModalOpen() || dragState) return;

        const year = selectedDate.getFullYear();
        const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(selectedDate.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
        let url = `/api/appointments?date=${dateStr}`;
        if (currentDoctorFilter) url += `&doctor_id=${currentDoctorFilter}`;

        fetch(url)
            .then(r => r.json())
            .then(newData => {
                if (_isAnyModalOpen() || dragState) return;
                const changed = JSON.stringify(newData) !== JSON.stringify(appointmentsList);
                appointmentsList = newData;
                renderDayView();
                _updateLastUpdatedLabel();
                if (changed && calendar && currentView === 'month') calendar.refetchEvents();
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

    // Busca com Enter + foco automático ao abrir o modal (leitura
    // apenas; abre /prontuario/dp/<id> e não cria agendamento).
    (function initPatientSearchUX() {
        const input = document.getElementById('patientSearchInput');
        const modalEl = document.getElementById('searchPatientModal');
        if (input) {
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    window.searchPatientsDetailed();
                }
            });
        }
        if (modalEl) {
            modalEl.addEventListener('shown.bs.modal', function() {
                if (input) { input.focus(); input.select(); }
            });
        }
    })();

    window.searchPatientsDetailed = function() {
        const q = document.getElementById('patientSearchInput').value.trim();
        if (q.length < 2) return;
        const body = document.getElementById('patientSearchResults');
        body.innerHTML = '<tr><td colspan="6">Buscando...</td></tr>';

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
                        <td>${p.patient_phone || '-'}</td>
                        <td>${p.patient_cpf || '-'}</td>
                        <td>Dr(a). ${p.doctor_name} (${p.doctor_role || 'DERM'})</td>
                        <td><button class="btn btn-sm btn-primary" onclick="goToPatientChart(${p.patient_id}, null, ${p.dp_id})">Prontuário</button></td>
                    </tr>`).join('') : '<tr><td colspan="6">Nenhum encontrado</td></tr>';
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
                <div class="waiting-patient-item" data-checkedin="${p.checked_in_time || ''}" onclick="goToPatientChart(${p.patient_id}, ${p.appointment_id})">
                    <span class="waiting-patient-name">${p.patient_name}</span>
                    <span class="waiting-patient-time"><span data-role="wait">${(p.wait_time_minutes ?? 0)} min</span></span>
                </div>`).join('') : '<div class="waiting-empty">Sala de espera vazia</div>';
            const countBadge = document.getElementById('waitingCountBadge');
            if (countBadge) countBadge.textContent = items.length;
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
                        ${APPOINTMENT_TYPES.map(type => `<option value="${type}" ${props.appointmentType === type ? 'selected' : ''}>${type}</option>`).join('')}
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
            if (dayContent) dayContent.style.display = '';
            if (monthContent) monthContent.style.display = 'none';
            if (dayBtn) dayBtn.classList.add('active');
            if (monthBtn) monthBtn.classList.remove('active');
        } else {
            if (dayContent) dayContent.style.display = 'none';
            if (monthContent) monthContent.style.display = 'block';
            if (dayBtn) dayBtn.classList.remove('active');
            if (monthBtn) monthBtn.classList.add('active');
            if (!calendar) initializeMonthCalendar();
            else {
                calendar.refetchEvents();
                calendar.updateSize();
            }
        }
        const nextCard = document.getElementById('agNextCard');
        if (nextCard) nextCard.style.display = view === 'day' ? '' : 'none';
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

function getActivationRequiredValues() {
    const phoneInput = document.getElementById('ativarTelefonePaciente');
    const cpfInput = document.getElementById('ativarCpfPaciente');
    return {
        phone: (phoneInput?.value || '').trim(),
        cpf: (cpfInput?.value || '').trim()
    };
}

function validateActivationRequiredFields() {
    const values = getActivationRequiredValues();
    const phoneError = document.getElementById('ativarTelefoneErro');
    const cpfError = document.getElementById('ativarCpfErro');
    const phoneInput = document.getElementById('ativarTelefonePaciente');
    const cpfInput = document.getElementById('ativarCpfPaciente');

    phoneError?.classList.toggle('d-none', !!values.phone);
    cpfError?.classList.toggle('d-none', !!values.cpf);

    if (!values.phone) {
        phoneInput?.focus();
        return null;
    }
    if (!values.cpf) {
        cpfInput?.focus();
        return null;
    }
    return values;
}

function setActivationDirectButtonState(pending, hasDuplicates = false) {
    const button = document.getElementById('ativarDiretoBtn');
    const label = document.getElementById('ativarDiretoBtnLabel');
    if (!button || !label) return;

    button.disabled = !!pending;
    button.classList.toggle('btn-success', !hasDuplicates);
    button.classList.toggle('btn-outline-danger', hasDuplicates);
    label.textContent = pending
        ? 'Verificando duplicidades...'
        : hasDuplicates
            ? 'Ignorar aviso e ativar como novo'
            : 'Ativar como novo paciente definitivo (gerar código)';
}

function renderActivationWarnings(data, patientId, doctorId) {
    const warnings = Array.isArray(data.warnings) ? data.warnings : [];
    window._ativarCtx.warnings = warnings;
    const alertaDiv = document.getElementById('ativarAlertas');
    const alertaMensagem = document.getElementById('ativarAlertasMensagem');
    const lista = document.getElementById('ativarAlertalista');
    const mergeDiv = document.getElementById('ativarMergeOpcoes');
    const mergeLista = document.getElementById('ativarMergeLista');
    const exactNameMatch = warnings.some(w => w.reason === 'nome_exato');
    const reasonLabels = {
        'nome_exato': 'Nome exatamente igual',
        'nome_semelhante': 'Nome semelhante',
        'mesmo_cpf': 'Mesmo CPF',
        'mesmo_telefone': 'Mesmo telefone'
    };

    alertaMensagem.textContent = exactNameMatch
        ? 'Existe um cadastro com o mesmo nome. Confira os dados antes de continuar.'
        : 'Encontramos cadastros com dados parecidos ou iguais. Confira cada resultado antes de continuar.';
    alertaDiv.classList.remove('d-none');
    mergeDiv.classList.remove('d-none');
    lista.replaceChildren();
    mergeLista.replaceChildren();

    warnings.forEach(warning => {
        const card = document.createElement('div');
        card.className = 'border rounded bg-white p-2 mb-2 small';

        const name = document.createElement('strong');
        name.textContent = warning.name || 'Paciente sem nome';
        card.appendChild(name);

        const identifiers = document.createElement('div');
        identifiers.className = 'text-muted';
        const identityParts = [`Cadastro #${warning.id}`];
        if (warning.patient_code !== null && warning.patient_code !== undefined) {
            identityParts.push(`Código ${warning.patient_code}`);
        }
        identifiers.textContent = identityParts.join(' · ');
        card.appendChild(identifiers);

        const reasons = Array.isArray(warning.match_reasons) && warning.match_reasons.length
            ? warning.match_reasons
            : [warning.reason];
        const badges = document.createElement('div');
        badges.className = 'mt-1';
        reasons.forEach(reason => {
            const badge = document.createElement('span');
            badge.className = `badge ${reason === 'nome_exato' || reason === 'mesmo_cpf' ? 'bg-danger' : 'bg-secondary'} me-1`;
            badge.textContent = reasonLabels[reason] || reason || 'Possível correspondência';
            badges.appendChild(badge);
        });
        card.appendChild(badges);

        const details = [];
        if (warning.phone) details.push(`Telefone: ${warning.phone}`);
        if (warning.cpf) details.push(`CPF: ${warning.cpf}`);
        if (warning.birth_date) {
            const rawDate = String(warning.birth_date).slice(0, 10);
            const parsedDate = new Date(`${rawDate}T00:00:00`);
            details.push(`Nascimento: ${Number.isNaN(parsedDate.getTime()) ? rawDate : parsedDate.toLocaleDateString('pt-BR')}`);
        }
        if (details.length) {
            const detailLine = document.createElement('div');
            detailLine.className = 'mt-1';
            detailLine.textContent = details.join(' · ');
            card.appendChild(detailLine);
        }
        lista.appendChild(card);

        const mergeButton = document.createElement('button');
        mergeButton.type = 'button';
        mergeButton.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2';

        const mergeLabel = document.createElement('span');
        mergeLabel.className = 'me-2';
        mergeLabel.textContent = `Vincular ao cadastro #${warning.id} — ${warning.name || 'Paciente sem nome'}`;
        mergeButton.appendChild(mergeLabel);

        const mergeBadge = document.createElement('span');
        mergeBadge.className = 'badge bg-primary';
        mergeBadge.textContent = 'Vincular';
        mergeButton.appendChild(mergeBadge);
        mergeButton.addEventListener('click', () => {
            const values = validateActivationRequiredFields();
            if (!values) return;
            _finalizarAtivacao(
                patientId, doctorId, warning.id, true, values.phone, values.cpf
            );
        });
        mergeLista.appendChild(mergeButton);
    });

    document.getElementById('ativarInstrucao').textContent =
        'A opção recomendada é vincular ao cadastro correto. Se confirmar que são pessoas diferentes, você poderá ignorar o aviso e receberá uma confirmação adicional.';
    setActivationDirectButtonState(false, warnings.length > 0);
}

window.abrirModalAtivacao = function(patientId, patientName, doctorId, existingPhone, existingCpf) {
    window._ativarCtx = { patientId, doctorId, warnings: [] };

    document.getElementById('ativarNomePaciente').textContent = patientName;
    const telInput = document.getElementById('ativarTelefonePaciente');
    const cpfInput = document.getElementById('ativarCpfPaciente');
    telInput.value = existingPhone || '';
    cpfInput.value = existingCpf || '';
    document.getElementById('ativarTelefoneErro').classList.add('d-none');
    document.getElementById('ativarCpfErro').classList.add('d-none');
    document.getElementById('ativarAlertas').classList.add('d-none');
    document.getElementById('ativarAlertasMensagem').textContent = '';
    document.getElementById('ativarAlertalista').innerHTML = '';
    document.getElementById('ativarMergeOpcoes').classList.add('d-none');
    document.getElementById('ativarMergeLista').innerHTML = '';
    document.getElementById('ativarInstrucao').textContent =
        'Verificando duplicidades...';
    setActivationDirectButtonState(true, false);

    if (!doctorId) {
        doctorId = window.currentDoctorId;
        window._ativarCtx.doctorId = doctorId;
    }

    // Verifica requisitos e duplicidades sem ativar o cadastro.
    fetch(`/api/patients/${patientId}/activation-preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        body: JSON.stringify({ doctor_id: doctorId, phone: existingPhone, cpf: existingCpf })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            document.getElementById('ativarInstrucao').textContent =
                'Revise os dados e confirme para ativar como novo paciente definitivo.';
            setActivationDirectButtonState(false, false);
            return;
        }
        if (data.error === 'required_fields' || data.error === 'phone_required' || data.error === 'cpf_required') {
            document.getElementById('ativarInstrucao').textContent =
                data.message || 'Informe telefone e CPF do paciente para ativar.';
            (data.required || []).forEach(item => {
                if (item.field === 'phone') document.getElementById('ativarTelefoneErro').classList.remove('d-none');
                if (item.field === 'cpf') document.getElementById('ativarCpfErro').classList.remove('d-none');
            });
            setActivationDirectButtonState(false, false);
            return;
        }
        if (data.warning === 'duplicates_found') {
            renderActivationWarnings(data, patientId, doctorId);
        } else if (data.error) {
            document.getElementById('ativarInstrucao').textContent =
                'Não foi possível concluir a verificação. Feche e abra novamente antes de ativar.';
            showAlert(data.error, 'danger');
        }
    })
    .catch(() => {
        document.getElementById('ativarInstrucao').textContent =
            'Não foi possível verificar duplicidades. Feche e abra novamente antes de ativar.';
        showAlert('Erro ao verificar duplicados', 'danger');
    });

    const modal = new bootstrap.Modal(document.getElementById('ativarProvisiorioModal'));
    modal.show();

    document.getElementById('ativarDiretoBtn').onclick = function() {
        const ctx = window._ativarCtx;
        const values = validateActivationRequiredFields();
        if (!values) {
            return;
        }
        document.getElementById('ativarTelefoneErro').classList.add('d-none');
        document.getElementById('ativarCpfErro').classList.add('d-none');
        const forceActivation = (ctx.warnings || []).length > 0;
        if (forceActivation) {
            const matches = ctx.warnings
                .slice(0, 3)
                .map(warning => `• ${warning.name || 'Paciente'} (cadastro #${warning.id})`)
                .join('\n');
            const confirmed = window.confirm(
                `Há possível duplicidade:\n${matches}\n\n` +
                'Criar outro cadastro pode dividir o prontuário e o histórico do paciente. ' +
                'Confirma que são pessoas diferentes e deseja continuar?'
            );
            if (!confirmed) return;
        }
        _finalizarAtivacao(
            ctx.patientId, ctx.doctorId, null, forceActivation,
            values.phone, values.cpf,
            forceActivation ? ctx.warnings.map(warning => warning.id) : []
        );
    };
};

window._finalizarAtivacao = function(
    patientId, doctorId, mergeIntoId, force, phone, cpf, confirmedDuplicateIds = []
) {
    const payload = { doctor_id: doctorId, force: !!force };
    if (mergeIntoId) payload.merge_into_patient_id = mergeIntoId;
    if (phone) payload.phone = phone;
    if (cpf) payload.cpf = cpf;
    if (Array.isArray(confirmedDuplicateIds) && confirmedDuplicateIds.length) {
        payload.confirmed_duplicate_patient_ids = confirmedDuplicateIds;
    }

    setActivationDirectButtonState(true, (window._ativarCtx.warnings || []).length > 0);
    document.querySelectorAll('#ativarMergeLista button').forEach(button => {
        button.disabled = true;
    });

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
                } else if (data.error === 'required_fields') {
                    (data.required || []).forEach(item => {
                        if (item.field === 'phone') document.getElementById('ativarTelefoneErro').classList.remove('d-none');
                        if (item.field === 'cpf') document.getElementById('ativarCpfErro').classList.remove('d-none');
                    });
                    setActivationDirectButtonState(false, (window._ativarCtx.warnings || []).length > 0);
                    showAlert(data.message || 'Informe telefone e CPF antes de ativar.', 'danger');
                } else {
                    setActivationDirectButtonState(false, (window._ativarCtx.warnings || []).length > 0);
                    document.querySelectorAll('#ativarMergeLista button').forEach(button => {
                        button.disabled = false;
                    });
                    showAlert(data.error || 'Erro ao ativar cadastro', 'danger');
                }
    })
    .catch(() => {
        setActivationDirectButtonState(false, (window._ativarCtx.warnings || []).length > 0);
        document.querySelectorAll('#ativarMergeLista button').forEach(button => {
            button.disabled = false;
        });
        showAlert('Erro ao ativar cadastro', 'danger');
    });
};
