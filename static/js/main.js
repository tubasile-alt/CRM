const originalFetch = window.fetch;

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

window.getCSRFToken = getCsrfToken;

function fetchWithCsrf(url, options = {}) {
    if (!options.headers) {
        options.headers = {};
    }
    
    if (options.method && options.method !== 'GET') {
        options.headers['X-CSRFToken'] = getCsrfToken();
    }
    
    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
    }
    
    return originalFetch(url, options);
}

window.fetch = fetchWithCsrf;

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatDateTime(date) {
    return new Date(date).toLocaleString('pt-BR');
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('pt-BR');
}

function formatTime(date) {
    return new Date(date).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

let lastUnreadCount = parseInt(localStorage.getItem('chatLastUnreadCount') || '0');
let lastNotifiedAt = 0;

function updateChatBadge() {
    const badge = document.getElementById('chat-badge');
    if (!badge) return;
    
    fetch('/api/chat/unread_count')
        .then(response => response.json())
        .then(data => {
            const count = data.count;
            badge.textContent = count;
            
            if (count > 0) {
                badge.style.display = 'inline-block';
                // Notificar se houver aumento
                if (count > lastUnreadCount) {
                    handleChatNotification(count);
                }
            } else {
                badge.style.display = 'none';
            }
            lastUnreadCount = count;
            localStorage.setItem('chatLastUnreadCount', lastUnreadCount);
        })
        .catch(error => {
            console.error('Erro ao atualizar badge do chat:', error);
        });
}

// Gerenciador de Notificações de Chat
function handleChatNotification(currentCount) {
    const now = Date.now();
    if (now - lastNotifiedAt < 4000) return; // Throttling 4s
    lastNotifiedAt = now;

    fetch('/api/chat/latest_unread')
        .then(res => res.json())
        .then(data => {
            const title = "Nova mensagem no chat";
            const body = data.id ? `De: ${data.from_name}\n${data.message}` : "Você tem novas mensagens não lidas.";
            
            // 1. Toast (Bootstrap)
            showChatToast(data.from_name || "Sistema", data.message || "Nova mensagem recebida");

            // 2. Notification API (se em background ou fora do chat)
            if (document.hidden || window.location.pathname !== '/chat') {
                if (Notification.permission === "granted") {
                    new Notification(title, { body: body, icon: '/static/images/logo-basile.jpg' });
                } else if (Notification.permission !== "denied") {
                    Notification.requestPermission();
                }
            }

            // 3. Som
            if (localStorage.getItem('chatSoundEnabled') === 'true') {
                playChatBeep();
            }
        });
}

function showChatToast(sender, message) {
    let container = document.getElementById('toast-container-chat');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container-chat';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast show shadow-lg" role="alert" aria-live="assertive" aria-atomic="true" style="cursor:pointer; min-width: 250px; background: white; border-left: 5px solid #0d6efd; margin-bottom: 10px;">
            <div class="toast-header">
                <strong class="me-auto"><i class="bi bi-chat-fill text-primary"></i> ${sender}</strong>
                <small>Agora</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    
    toastElement.onclick = (e) => {
        if (!e.target.classList.contains('btn-close')) {
            window.location.href = '/chat';
        }
    };
    
    setTimeout(() => {
        if (toastElement && toastElement.parentElement) toastElement.remove();
    }, 5000);
}

function playChatBeep() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.1);
    } catch (e) {
        console.error("Erro ao tocar som:", e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const soundToggle = document.getElementById('toggle-chat-sound');
    const soundIcon = document.getElementById('chat-sound-icon');
    
    if (soundToggle) {
        const updateIcon = (enabled) => {
            soundIcon.className = enabled ? 'bi bi-volume-up-fill text-success' : 'bi bi-volume-mute text-secondary';
        };

        let enabled = localStorage.getItem('chatSoundEnabled') === 'true';
        updateIcon(enabled);

        soundToggle.onclick = (e) => {
            e.preventDefault();
            enabled = !enabled;
            localStorage.setItem('chatSoundEnabled', enabled);
            updateIcon(enabled);
            if (enabled) playChatBeep(); // Teste ao ativar
        };
    }

    // Solicitar permissão de notificação
    if (Notification.permission !== "granted" && Notification.permission !== "denied") {
        Notification.requestPermission();
    }
});

if (document.getElementById('chat-badge')) {
    updateChatBadge();
    setInterval(updateChatBadge, 5000);
}
