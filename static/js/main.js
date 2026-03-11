const originalFetch = window.fetch;

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

window.getCSRFToken = getCsrfToken;

async function fetchWithCSRF(url, options = {}) {
    const opts = { credentials: 'same-origin', ...options };
    const method = (opts.method || 'GET').toUpperCase();
    opts.headers = { ...(opts.headers || {}) };

    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        opts.headers['X-CSRFToken'] = getCsrfToken();
        if (!opts.headers['Content-Type'] && !(opts.body instanceof FormData)) {
            opts.headers['Content-Type'] = 'application/json';
        }
    }
    
    return originalFetch(url, opts);
}

window.fetchWithCSRF = fetchWithCSRF;
window.fetch = fetchWithCSRF;

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

const ChatNotifier = {
    activePopupId: null,
    popupAutoCloseMs: 12000,

    playIcqAlert() {
        try {
            if (!(window.AudioContext || window.webkitAudioContext)) return;

            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const now = audioCtx.currentTime;
            const notes = [740, 988, 740];

            notes.forEach((frequency, index) => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(frequency, now + index * 0.12);
                gain.gain.setValueAtTime(0.0001, now + index * 0.12);
                gain.gain.exponentialRampToValueAtTime(0.15, now + index * 0.12 + 0.02);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + index * 0.12 + 0.1);

                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now + index * 0.12);
                osc.stop(now + index * 0.12 + 0.11);
            });
        } catch (e) {
            console.error('[ChatNotifier] Erro ao tocar alerta ICQ-like:', e);
        }
    },

    showUrgentPopup(data) {
        if (!data || !data.id) return;

        const oldPopup = document.getElementById('chat-urgent-popup');
        if (oldPopup) oldPopup.remove();

        const popup = document.createElement('div');
        popup.id = 'chat-urgent-popup';
        popup.style.cssText = `
            position: fixed;
            top: 22px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 100000;
            width: min(520px, calc(100vw - 24px));
            background: linear-gradient(135deg, #0b5ed7 0%, #0a3ea9 100%);
            color: #fff;
            border-radius: 14px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255,255,255,0.2);
            padding: 16px;
            animation: chatPulseIn .28s ease-out;
        `;

        popup.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                <div>
                    <div style="font-size: 15px; font-weight: 700; letter-spacing: .2px;">
                        <i class="bi bi-bell-fill"></i> Nova mensagem para responder
                    </div>
                    <div style="font-size: 13px; opacity: .9; margin-top: 2px;">${data.from_name || 'Contato'} acabou de te chamar.</div>
                </div>
                <button id="chat-urgent-close" class="btn btn-sm btn-light" style="line-height:1;">Fechar</button>
            </div>
            <div style="margin-top: 10px; background: rgba(255,255,255,.12); border-radius: 10px; padding: 10px 12px;">
                <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">${data.from_name || 'Contato'}</div>
                <div style="font-size: 14px; line-height: 1.35;">${data.message || ''}</div>
            </div>
            <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:12px;">
                <button id="chat-open-now" class="btn btn-warning btn-sm fw-semibold">Responder agora</button>
            </div>
        `;

        document.body.appendChild(popup);
        this.activePopupId = data.id;

        const closePopup = () => {
            if (popup && popup.parentNode) popup.remove();
            this.activePopupId = null;
        };

        document.getElementById('chat-open-now')?.addEventListener('click', () => {
            window.location.href = '/chat';
        });

        document.getElementById('chat-urgent-close')?.addEventListener('click', closePopup);

        setTimeout(() => {
            if (this.activePopupId === data.id) closePopup();
        }, this.popupAutoCloseMs);
    },

    notifyIncomingInActiveChat(msg) {
        this.showUrgentPopup({
            id: `live-${msg.id || Date.now()}`,
            from_name: msg.from_name || 'Contato',
            message: msg.message
        });
        if (localStorage.getItem('chatSoundEnabled') === 'true') {
            this.playIcqAlert();
        }
    }
};

window.ChatNotifier = ChatNotifier;

if (!document.getElementById('chat-notifier-inline-style')) {
    const style = document.createElement('style');
    style.id = 'chat-notifier-inline-style';
    style.textContent = '@keyframes chatPulseIn { from { opacity:0; transform:translate(-50%, -8px);} to { opacity:1; transform:translate(-50%, 0);} }';
    document.head.appendChild(style);
}

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
        .then(response => {
            if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) {
                throw new Error('Sessão expirada ou erro no servidor');
            }
            return response.json();
        })
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

            showToastNotification(data);
            ChatNotifier.showUrgentPopup(data);

            if (document.hidden || window.location.pathname !== '/chat') {
                if (Notification.permission === "granted") {
                    new Notification("Nova mensagem de " + data.from_name, { body: data.message });
                }
            }
            if (localStorage.getItem('chatSoundEnabled') === 'true') {
                ChatNotifier.playIcqAlert();
            }
        });
}

function showToastNotification(data) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    if (!(window.bootstrap && bootstrap.Toast)) {
        console.warn("[ChatNotifier] Bootstrap Toast não disponível");
        return;
    }

    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-primary text-white">
                <i class="bi bi-chat-dots me-2"></i>
                <strong class="me-auto">Nova mensagem — ${data.from_name}</strong>
                <small>Agora</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body" style="cursor: pointer;" onclick="window.location.href='/chat'">
                ${data.message}
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function playChatBeep() {
    ChatNotifier.playIcqAlert();
}

function initChatNotifier() {
    // Configurar toggle de som
    const soundToggle = document.getElementById('toggle-chat-sound');
    const soundIcon = document.getElementById('chat-sound-icon');

    if (soundToggle && soundIcon) {
        const updateIcon = (enabled) => {
            soundIcon.className = enabled ? 'bi bi-volume-up-fill text-success' : 'bi bi-volume-mute text-secondary';
        };

        const savedSound = localStorage.getItem('chatSoundEnabled');
        let enabled = savedSound === null ? true : savedSound === 'true';
        if (savedSound === null) localStorage.setItem('chatSoundEnabled', 'true');
        updateIcon(enabled);

        soundToggle.onclick = (e) => {
            e.preventDefault();
            enabled = !enabled;
            localStorage.setItem('chatSoundEnabled', enabled);
            updateIcon(enabled);
            
            // Mostrar toast de confirmação
            showToastNotification({
                from_name: 'Sistema',
                message: 'Som do chat: ' + (enabled ? 'ATIVADO' : 'DESATIVADO')
            });
            
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
    try {
        initChatNotifier();
    } catch (e) {
        console.error('[ChatNotifier] Erro de inicialização:', e);
    }
}

// Iniciar com segurança
startChatNotifier();

window.addEventListener('load', startChatNotifier);

console.log('[main.js] loaded');
