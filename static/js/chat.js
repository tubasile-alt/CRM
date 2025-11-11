let lastMessageId = 0;
const currentUserId = parseInt(document.body.dataset.userId || '0');

function loadMessages() {
    fetch('/api/chat/messages')
        .then(response => response.json())
        .then(messages => {
            const chatDiv = document.getElementById('chatMessages');
            chatDiv.innerHTML = '';
            
            messages.forEach(msg => {
                const isSent = msg.senderId === currentUserId;
                const msgDiv = document.createElement('div');
                msgDiv.className = `chat-message ${isSent ? 'sent' : 'received'}`;
                msgDiv.innerHTML = `
                    <div class="message-sender">${msg.sender}</div>
                    <div class="message-text">${escapeHtml(msg.message)}</div>
                    <div class="message-time">${msg.timestamp}</div>
                `;
                chatDiv.appendChild(msgDiv);
                lastMessageId = Math.max(lastMessageId, msg.id);
            });
            
            chatDiv.scrollTop = chatDiv.scrollHeight;
            markMessagesAsRead();
        })
        .catch(error => {
            console.error('Erro ao carregar mensagens:', error);
        });
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    fetch('/api/chat/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(() => {
        input.value = '';
        loadMessages();
    })
    .catch(error => {
        console.error('Erro ao enviar mensagem:', error);
        showAlert('Erro ao enviar mensagem.', 'danger');
    });
}

function markMessagesAsRead() {
    fetch('/api/chat/mark_read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(() => {
        if (typeof updateChatBadge === 'function') {
            updateChatBadge();
        }
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

loadMessages();
setInterval(loadMessages, 5000);
