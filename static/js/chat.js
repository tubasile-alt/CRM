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
      
      const withUserId = parseInt(selectedContactId, 10);
      const messagesArea = document.getElementById('messagesArea');
      if (!messagesArea) return;

      fetch(`/api/chat/messages?with_user_id=${withUserId}&t=${Date.now()}`)
          .then(response => {
              if (!response.ok) throw new Error('Erro ao carregar');
              return response.json();
          })
          .then(messages => {
              const currentUserId = parseInt(document.body.dataset.userId || '0', 10);

              // 1. Coletar mensagens locais (temporárias)
              const localMsgs = Array.from(messagesArea.querySelectorAll('.chat-message[id^="temp-"]')).map(el => ({
                  id: el.id,
                  html: el.innerHTML,
                  text: el.querySelector('.message-text').textContent.trim()
              }));

              // 2. IDs do servidor
              const serverIds = messages.map(m => m.id.toString());
              const currentOfficialIds = Array.from(messagesArea.querySelectorAll('.chat-message:not([id^="temp-"])')).map(el => el.dataset.msgId);
              
              const serverTexts = new Set(messages.filter(m => parseInt(m.senderId, 10) === currentUserId).map(m => m.message.trim()));

              // Se nada mudou no servidor e não temos novas locais, não faz nada
              if (serverIds.join(',') === currentOfficialIds.join(',') && localMsgs.length === 0 && messages.length > 0) return;

              // 3. Reconstruir
              messagesArea.innerHTML = '';
              
              // Renderiza oficiais
              messages.forEach(msg => {
                  appendMessageToUI({
                      senderId: msg.senderId,
                      message: msg.message,
                      timestamp: msg.timestamp,
                      id: msg.id
                  }, false);
              });
              
              // Re-insere locais pendentes
              localMsgs.forEach(local => {
                  if (!serverTexts.has(local.text)) {
                      const msgDiv = document.createElement('div');
                      msgDiv.className = 'chat-message sent';
                      msgDiv.id = local.id;
                      msgDiv.innerHTML = local.html;
                      messagesArea.appendChild(msgDiv);
                  }
              });
              
              messagesArea.scrollTop = messagesArea.scrollHeight;
          })
          .catch(err => console.error('Erro polling:', err));
  }

  function sendMessage() {
      if (!selectedContactId) {
          showAlert('Selecione um contato primeiro.', 'warning');
          return;
      }
      
      const input = document.getElementById('messageInput');
      const message = input.value.trim();
      if (!message) return;
      
      const currentUserId = parseInt(document.body.dataset.userId || '0', 10);
      const tempId = 'temp-' + Date.now();
      
      // Mostra na hora
      appendMessageToUI({
          senderId: currentUserId,
          message: message,
          timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
          id: tempId
      });
      
      input.value = '';
      input.focus();
      
      fetch('/api/chat/send', {
          method: 'POST',
          body: JSON.stringify({ recipient_id: selectedContactId, message: message })
      })
      .then(res => res.json())
      .then(data => {
          if (!data.success) {
              const temp = document.getElementById(tempId);
              if (temp) temp.remove();
              showAlert(data.error || 'Erro ao enviar', 'danger');
          }
      })
      .catch(() => {
          const temp = document.getElementById(tempId);
          if (temp) temp.remove();
          showAlert('Erro de conexão', 'danger');
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
