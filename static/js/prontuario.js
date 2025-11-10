let timerInterval = null;
let timerStartTime = null;
let recognition = null;
let activeTextarea = null;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.continuous = true;
    recognition.interimResults = true;
    
    recognition.onresult = function(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        if (activeTextarea && finalTranscript) {
            activeTextarea.value += finalTranscript;
        }
    };
    
    recognition.onerror = function(event) {
        console.error('Erro no reconhecimento de voz:', event.error);
        stopDictation();
        showAlert('Erro no reconhecimento de voz. Verifique se o microfone está habilitado.', 'danger');
    };
    
    recognition.onend = function() {
        stopDictation();
    };
}

function startDictation(textareaId) {
    if (!recognition) {
        showAlert('Reconhecimento de voz não suportado neste navegador.', 'warning');
        return;
    }
    
    activeTextarea = document.getElementById(textareaId);
    const button = event.target.closest('button');
    
    if (button.classList.contains('dictation-active')) {
        stopDictation();
    } else {
        try {
            recognition.start();
            button.classList.add('dictation-active');
            button.innerHTML = '<i class="bi bi-mic-fill"></i> Gravando...';
        } catch (error) {
            console.error('Erro ao iniciar ditado:', error);
            showAlert('Erro ao iniciar ditado.', 'danger');
        }
    }
}

function stopDictation() {
    if (recognition) {
        recognition.stop();
    }
    
    const buttons = document.querySelectorAll('.dictation-active');
    buttons.forEach(button => {
        button.classList.remove('dictation-active');
        button.innerHTML = '<i class="bi bi-mic"></i> Ditado';
    });
    
    activeTextarea = null;
}

function startConsultation() {
    const button = document.getElementById('startTimer');
    const display = document.getElementById('timerDisplay');
    
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        button.innerHTML = '<i class="bi bi-play-circle"></i> Iniciar Atendimento';
        button.classList.remove('btn-danger');
        button.classList.add('btn-success');
        display.classList.remove('timer-running');
    } else {
        timerStartTime = Date.now();
        button.innerHTML = '<i class="bi bi-stop-circle"></i> Parar Atendimento';
        button.classList.remove('btn-success');
        button.classList.add('btn-danger');
        display.classList.add('timer-running');
        
        timerInterval = setInterval(updateTimer, 1000);
        updateTimer();
    }
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - timerStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    
    document.getElementById('timerDisplay').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function getConsultationDuration() {
    if (timerStartTime) {
        return Math.floor((Date.now() - timerStartTime) / 60000);
    }
    return null;
}

function saveNote(noteType) {
    const textareaId = `${noteType}Text`;
    const content = document.getElementById(textareaId).value.trim();
    
    if (!content) {
        showAlert('Por favor, adicione algum conteúdo antes de salvar.', 'warning');
        return;
    }
    
    const data = {
        type: noteType,
        content: content,
        duration: getConsultationDuration()
    };
    
    if (noteType === 'anamnese') {
        const indicatedProcs = Array.from(document.querySelectorAll('.indicated-proc:checked'))
            .map(cb => parseInt(cb.value));
        if (indicatedProcs.length > 0) {
            data.indicated_procedures = indicatedProcs;
        }
    }
    
    if (noteType === 'conduta') {
        const performedProcs = Array.from(document.querySelectorAll('.performed-proc:checked'))
            .map(cb => parseInt(cb.value));
        if (performedProcs.length > 0) {
            data.performed_procedures = performedProcs;
        }
    }
    
    fetch(`/api/prontuario/${patientId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Anotação salva com sucesso!');
            document.getElementById(textareaId).value = '';
            
            if (noteType === 'anamnese') {
                document.querySelectorAll('.indicated-proc').forEach(cb => cb.checked = false);
            }
            if (noteType === 'conduta') {
                document.querySelectorAll('.performed-proc').forEach(cb => cb.checked = false);
            }
            
            setTimeout(() => location.reload(), 1500);
        }
    })
    .catch(error => {
        showAlert('Erro ao salvar anotação.', 'danger');
        console.error(error);
    });
}

function savePatientTags() {
    const selectedTags = Array.from(document.querySelectorAll('.tag-checkbox:checked'))
        .map(cb => parseInt(cb.value));
    
    fetch(`/api/patient/${patientId}/tags`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tags: selectedTags })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Tags atualizadas com sucesso!');
        }
    })
    .catch(error => {
        showAlert('Erro ao atualizar tags.', 'danger');
        console.error(error);
    });
}
