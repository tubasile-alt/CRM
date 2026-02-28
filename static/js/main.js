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
let lastSeenMessageId = localStorage.getItem('chatLastSeenMessageId');

const miniChatDockStyles = `
<style>
.mini-chat-dock {
    position: fixed;
    bottom: 16px;
    right: 16px;
    width: 320px;
    z-index: 9999;
    display: flex;
    flex-direction: column-reverse;
    gap: 10px;
    pointer-events: none;
}
.mini-chat-card {
    pointer-events: auto;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border: 1px solid #dee2e6;
    overflow: hidden;
    animation: slideIn 0.3s ease-out;
}
@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
.mini-chat-header {
    background: #0d6efd;
    color: white;
    padding: 8px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
}
.mini-chat-body {
    padding: 10px;
    max-height: 150px;
    overflow-y: auto;
    font-size: 0.9rem;
    white-space: pre-wrap;
    word-break: break-word;
}
.mini-chat-footer {
    padding: 8px;
    border-top: 1px solid #eee;
    display: flex;
    gap: 5px;
}
.mini-chat-input {
    flex: 1;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 0.85rem;
    resize: none;
}
</style>
`;

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
                if (count > lastUnreadCount) {
                    handleChatNotification(count);
                }
            } else {
                badge.style.display = 'none';
            }
            lastUnreadCount = count;
            localStorage.setItem('chatLastUnreadCount', lastUnreadCount);
        })
        .catch(error => console.error('Erro badge:', error));
}

function handleChatNotification(currentCount) {
    const now = Date.now();
    if (now - lastNotifiedAt < 4000) return;
    lastNotifiedAt = now;

    fetch('/api/chat/latest_unread')
        .then(res => res.json())
        .then(data => {
            if (!data.id || data.id == lastSeenMessageId) return;
            
            lastSeenMessageId = data.id;
            localStorage.setItem('chatLastSeenMessageId', lastSeenMessageId);

            showMiniChatPopup(data);

            if (document.hidden || window.location.pathname !== '/chat') {
                if (Notification.permission === "granted") {
                    new Notification("Nova mensagem de " + data.from_name, { body: data.message });
                }
            }
            if (localStorage.getItem('chatSoundEnabled') === 'true') {
                playChatBeep();
            }
        });
}

function showMiniChatPopup(data) {
    let dock = document.getElementById('miniChatDock');
    if (!dock) {
        document.head.insertAdjacentHTML('beforeend', miniChatDockStyles);
        dock = document.createElement('div');
        dock.id = 'miniChatDock';
        dock.className = 'mini-chat-dock';
        document.body.appendChild(dock);
    }

    if (dock.children.length >= 3) {
        dock.lastElementChild.remove();
    }

    const cardId = 'mini-chat-' + data.id;
    if (document.getElementById(cardId)) return;

    const card = document.createElement('div');
    card.id = cardId;
    card.className = 'mini-chat-card';
    card.innerHTML = `
        <div class="mini-chat-header" onclick="window.location.href='/chat'">
            <span><i class="bi bi-person-circle"></i> ${data.from_name}</span>
            <button class="btn-close btn-close-white" style="font-size: 0.7rem;"></button>
        </div>
        <div class="mini-chat-body">${data.message}</div>
        <div class="mini-chat-footer">
            <textarea class="mini-chat-input" placeholder="Responder..." rows="1"></textarea>
            <button class="btn btn-sm btn-primary btn-send">Enviar</button>
        </div>
        <div class="send-status text-success px-2 pb-1 small" style="display:none;">Enviado ✓</div>
    `;

    dock.prepend(card);

    const closeBtn = card.querySelector('.btn-close');
    closeBtn.onclick = (e) => { e.stopPropagation(); card.remove(); };

    const input = card.querySelector('.mini-chat-input');
    const sendBtn = card.querySelector('.btn-send');
    const status = card.querySelector('.send-status');

    let autoHideTimer = setTimeout(() => card.remove(), 20000);

    const resetTimer = () => {
        clearTimeout(autoHideTimer);
        autoHideTimer = setTimeout(() => card.remove(), 20000);
    };

    card.onmouseenter = () => clearTimeout(autoHideTimer);
    card.onmouseleave = resetTimer;
    input.onfocus = () => clearTimeout(autoHideTimer);

    sendBtn.onclick = () => {
        const text = input.value.trim();
        if (!text) return;

        sendBtn.disabled = true;
        fetch('/api/chat/send', {
            method: 'POST',
            body: JSON.stringify({ recipient_id: data.from_user_id, message: text })
        })
        .then(res => res.json())
        .then(resData => {
            if (resData.success) {
                status.style.display = 'block';
                input.value = '';
                setTimeout(() => card.remove(), 2000);
                // Marcar como lida ao responder
                fetch(`/api/chat/mark_read/${data.id}`, { method: 'POST' });
            } else {
                alert('Erro ao enviar');
                sendBtn.disabled = false;
            }
        });
    };
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

function initChatNotifier() {
    // Configurar toggle de som
    const soundToggle = document.getElementById('toggle-chat-sound');
    const soundIcon = document.getElementById('chat-sound-icon');

    if (soundToggle && soundIcon) {
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
            if (enabled) playChatBeep();
        };
    }

    // Solicitar permissão de notificação
    if (typeof Notification !== 'undefined' && Notification.permission !== "granted" && Notification.permission !== "denied") {
        Notification.requestPermission();
    }

    // Iniciar polling do badge/notificações
    updateChatBadge();
    setInterval(updateChatBadge, 5000);

    // Indicador de debug visual (canto inferior esquerdo)
    const debugEl = document.createElement('div');
    debugEl.id = 'chat-notifier-indicator';
    debugEl.style.cssText = 'position:fixed;bottom:8px;left:8px;background:#198754;color:#fff;font-size:11px;padding:3px 8px;border-radius:4px;z-index:99999;opacity:0.8;pointer-events:none;';
    debugEl.textContent = 'ChatNotifier ativo';
    document.body.appendChild(debugEl);
    setTimeout(() => { debugEl.style.display = 'none'; }, 8000);

    console.log('[ChatNotifier] Inicializado com sucesso.');
}

function startChatNotifier() {
    if (window.__chatNotifierStarted) return;
    window.__chatNotifierStarted = true;
    initChatNotifier();
}

// Iniciar imediatamente (script já está no final do body)
startChatNotifier();

// Fallback: garantir init após window.onload (caso haja race condition)
window.addEventListener('load', startChatNotifier);
