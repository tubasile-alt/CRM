let selectedContactId = null;
const currentUserId = parseInt(document.body.dataset.userId || '0');

function loadContacts() {
    fetch('/api/chat/contacts')
        .then(response => response.json())
        .then(contacts => {
            const listDiv = document.getElementById('contactsList');
            
            if (contacts.length === 0) {
                listDiv.innerHTML = `
                    <div style="padding: 20px; text-align: center; color: #6c757d;">
                        Nenhum contato disponível
                    </div>
                `;
                return;
            }
            
            listDiv.innerHTML = '';
            
            contacts.forEach(contact => {
                const contactItem = document.createElement('div');
                contactItem.className = `contact-item ${selectedContactId === contact.id ? 'active' : ''}`;
                contactItem.onclick = () => selectContact(contact.id, contact.name);
                
                let roleIcon = contact.role === 'medico' ? '👨‍⚕️' : '👩';
                let roleText = contact.role === 'medico' ? 'Médico' : 'Secretária';
                
                contactItem.innerHTML = `
                    <div class="contact-name">${roleIcon} ${contact.name}</div>
                    <div class="contact-role">${roleText}</div>
                    ${contact.unread_count > 0 ? `<span class="contact-badge">${contact.unread_count}</span>` : ''}
                `;
                
                listDiv.appendChild(contactItem);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar contatos:', error);
        });
}

function selectContact(contactId, contactName) {
    selectedContactId = contactId;
    
    const panel = document.getElementById('conversationPanel');
    panel.innerHTML = `
        <div class="conversation-header">
            <div class="conversation-title">${contactName}</div>
        </div>
        <div class="messages-area" id="messagesArea">
            <div style="text-align: center; padding: 20px; color: #6c757d;">
                Carregando mensagens...
            </div>
        </div>
        <div class="message-input-area">
            <div class="input-group">
                <input type="text" id="messageInput" class="form-control" placeholder="Digite sua mensagem...">
                <button class="btn btn-primary" onclick="sendMessage()">
                    <i class="bi bi-send"></i> Enviar
                </button>
            </div>
        </div>
    `;
    
    const inputField = document.getElementById('messageInput');
    inputField.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    loadContacts();
    loadMessages();
    markMessagesAsRead();
}

function loadMessages() {
    if (!selectedContactId) return;
    
    fetch(`/api/chat/messages?with_user_id=${selectedContactId}`)
        .then(response => response.json())
        .then(messages => {
            const messagesDiv = document.getElementById('messagesArea');
            messagesDiv.innerHTML = '';
            
            if (messages.length === 0) {
                messagesDiv.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #6c757d;">
                        <i class="bi bi-chat-left-text" style="font-size: 3rem; margin-bottom: 15px;"></i>
                        <p>Nenhuma mensagem ainda. Seja o primeiro a enviar!</p>
                    </div>
                `;
                return;
            }
            
            messages.forEach(msg => {
                const isSent = msg.senderId === currentUserId;
                const msgDiv = document.createElement('div');
                msgDiv.className = `chat-message ${isSent ? 'sent' : 'received'}`;
                msgDiv.innerHTML = `
                    <div class="message-text">${escapeHtml(msg.message)}</div>
                    <div class="message-time">${msg.timestamp}</div>
                `;
                messagesDiv.appendChild(msgDiv);
            });
            
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        })
        .catch(error => {
            console.error('Erro ao carregar mensagens:', error);
        });
}

function sendMessage() {
    if (!selectedContactId) {
        showAlert('Selecione um contato primeiro.', 'warning');
        return;
    }
    
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    fetch('/api/chat/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipient_id: selectedContactId,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            input.value = '';
            loadMessages();
        } else {
            showAlert(data.error || 'Erro ao enviar mensagem.', 'danger');
        }
    })
    .catch(error => {
        console.error('Erro ao enviar mensagem:', error);
        showAlert('Erro ao enviar mensagem.', 'danger');
    });
}

function markMessagesAsRead() {
    if (!selectedContactId) return;
    
    fetch('/api/chat/mark_read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            from_user_id: selectedContactId
        })
    }).then(() => {
        if (typeof updateChatBadge === 'function') {
            updateChatBadge();
        }
        loadContacts();
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

loadContacts();

setInterval(() => {
    if (selectedContactId) {
        loadMessages();
        markMessagesAsRead();
    }
    loadContacts();
}, 5000);
