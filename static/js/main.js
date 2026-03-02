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

            showToastNotification(data);

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
    try {
        if (!(window.AudioContext || window.webkitAudioContext)) {
            console.warn("[ChatNotifier] WebAudio não disponível");
            return;
        }
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


  // --- CHAT NOTIFIER SYSTEM ---
  let lastUnreadCount = parseInt(localStorage.getItem('chatLastUnreadCount') || '0');
  let lastNotifiedAt = parseInt(localStorage.getItem('chatLastNotifiedAt') || '0');
  let lastLatestMessageId = localStorage.getItem('chatLastLatestMessageId') || '';

  function playBeep() {
      try {
          if (localStorage.getItem('chatSoundEnabled') !== '1') return;
          const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
          const oscillator = audioCtx.createOscillator();
          const gainNode = audioCtx.createGain();
          oscillator.connect(gainNode);
          gainNode.connect(audioCtx.destination);
          oscillator.type = 'sine';
          oscillator.frequency.setValueAtTime(440, audioCtx.currentTime);
          gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
          oscillator.start();
          oscillator.stop(audioCtx.currentTime + 0.2);
      } catch (e) { console.error('Error playing beep:', e); }
  }

  function showToast(data) {
      const root = document.getElementById('chat-toast-root');
      if (!root) return;
      while (root.children.length >= 3) { root.removeChild(root.firstChild); }
      const toast = document.createElement('div');
      toast.className = 'chat-toast';
      toast.innerHTML = `
          <div class="x">&times;</div>
          <div class="t">Nova mensagem — ${data.from_name || 'Chat'}</div>
          <div class="b">${data.message || 'Você recebeu uma nova mensagem.'}</div>
      `;
      toast.onclick = (e) => {
          if (e.target.className === 'x') { toast.remove(); } 
          else { window.location.href = '/chat'; }
      };
      root.appendChild(toast);
      setTimeout(() => toast.classList.add('show'), 10);
      setTimeout(() => {
          toast.classList.remove('show');
          setTimeout(() => { if(toast.parentNode) toast.remove(); }, 200);
      }, 6000);
  }

  async function checkChat() {
      try {
          const r = await fetch('/api/chat/unread_count', { credentials: 'same-origin' });
          if (!r.ok) return;
          const { count } = await r.json();
          const badge = document.getElementById('chat-badge');
          if (badge) {
              badge.textContent = count;
              badge.style.display = count > 0 ? 'inline-block' : 'none';
          }
          if (count > lastUnreadCount) {
              const now = Date.now();
              if (now - lastNotifiedAt < 4000) {
                  lastUnreadCount = count;
                  localStorage.setItem('chatLastUnreadCount', String(count));
                  return;
              }
              const lr = await fetch('/api/chat/latest_unread', { credentials: 'same-origin' });
              if (!lr.ok) return;
              const latest = await lr.json();
              if (latest && latest.id && String(latest.id) !== String(lastLatestMessageId)) {
                  showToast(latest);
                  if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
                      new Notification('Nova mensagem — ' + (latest.from_name || 'Chat'), { body: latest.message || '' });
                  }
                  playBeep();
                  lastLatestMessageId = String(latest.id);
                  localStorage.setItem('chatLastLatestMessageId', lastLatestMessageId);
                  lastNotifiedAt = now;
                  localStorage.setItem('chatLastNotifiedAt', String(now));
              }
          }
          lastUnreadCount = count;
          localStorage.setItem('chatLastUnreadCount', String(count));
      } catch (e) { console.error('[CHAT NOTIFIER]', e); }
  }

  if (!window._chatCheckStarted) {
      window._chatCheckStarted = true;
      setInterval(checkChat, 5000);
      checkChat();
  }

  document.addEventListener('DOMContentLoaded', () => {
      const soundBtn = document.getElementById('toggle-chat-sound');
      if (soundBtn) {
          const icon = soundBtn.querySelector('i');
          const updateIcon = () => {
              const enabled = localStorage.getItem('chatSoundEnabled') === '1';
              if(icon) icon.className = enabled ? 'bi bi-volume-up-fill text-success' : 'bi bi-volume-mute text-secondary';
          };
          updateIcon();
          soundBtn.onclick = (e) => {
              e.preventDefault();
              const newState = localStorage.getItem('chatSoundEnabled') === '1' ? '0' : '1';
              localStorage.setItem('chatSoundEnabled', newState);
              updateIcon();
              if (newState === '1') playBeep();
          };
      }
  });