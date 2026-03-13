let selectedContactId = null;
  const currentUserId = parseInt(document.body.dataset.userId || '0');
  let knownMessageIds = new Set();
  let lastAlertedIncomingId = null;

  function loadContacts() {
      fetch('/api/chat/contacts')
          .then(response => {
              if (!response.ok) throw new Error('Falha ao carregar contatos (Status: ' + response.status + ')');
              return response.json();
          })
          .then(contacts => {
              if (typeof contacts === 'string' && contacts.includes('<!DOCTYPE')) {
                  console.error('[CHAT] Recebeu HTML em vez de JSON em loadContacts. Sessão expirada?');
                  return;
              }
              const listDiv = document.getElementById('contactsList');
              if (!listDiv) return;
              
              if (!Array.isArray(contacts) || contacts.length === 0) {
                  listDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #6c757d;">Nenhum contato disponível</div>';
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
          .catch(error => console.error('[CHAT] Erro ao carregar contatos:', error));
  }

  function selectContact(contactId, contactName) {
      console.log('[CHAT] Selecionando contato:', contactId, contactName);
      selectedContactId = contactId;
      knownMessageIds = new Set();
      lastAlertedIncomingId = null;
      const panel = document.getElementById('conversationPanel');
      if (!panel) return;

      panel.innerHTML = `
          <div class="conversation-header">
              <div class="conversation-title">${contactName}</div>
          </div>
          <div class="messages-area" id="messagesArea">
              <div style="text-align: center; padding: 20px; color: #6c757d;">Carregando mensagens...</div>
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
      if (inputField) {
          inputField.focus();
          inputField.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
      }
      
      loadContacts();
      loadMessages();
      markMessagesAsRead();
  }

  function appendMessageToUI(msg, shouldScroll = true) {
      const messagesArea = document.getElementById('messagesArea');
      if (!messagesArea) return;

      const placeholder = messagesArea.querySelector('div[style*="padding: 40px"]');
      if (placeholder) placeholder.remove();

      const isSent = parseInt(msg.senderId, 10) === currentUserId;
      
      const msgDiv = document.createElement('div');
      msgDiv.className = `chat-message ${isSent ? 'sent' : 'received'}`;
      msgDiv.id = msg.id && !msg.id.toString().startsWith('temp-') ? `msg-${msg.id}` : msg.id;
      msgDiv.dataset.msgId = msg.id;
      
      msgDiv.innerHTML = `
          <div class="message-text">${escapeHtml(msg.message)}</div>
          <div class="message-time">${msg.timestamp || 'agora'}</div>
      `;
      
      messagesArea.appendChild(msgDiv);
      if (shouldScroll) messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  function loadMessages() {
      if (!selectedContactId) return;
      
      const withUserId = parseInt(selectedContactId, 10);
      const messagesArea = document.getElementById('messagesArea');
      if (!messagesArea) return;

      fetch(`/api/chat/messages?with_user_id=${withUserId}&t=${Date.now()}`)
          .then(response => {
              if (!response.ok) throw new Error('Erro HTTP: ' + response.status);
              return response.json();
          })
          .then(messages => {
              if (typeof messages === 'string' && messages.includes('<!DOCTYPE')) {
                   console.warn('[CHAT] Erro polling: Resposta HTML recebida.');
                   return;
              }

              const incomingNewMessages = messages.filter(msg => {
                  const msgId = String(msg.id);
                  const isIncoming = parseInt(msg.senderId, 10) !== currentUserId;
                  return isIncoming && !knownMessageIds.has(msgId);
              });

              messages.forEach(msg => knownMessageIds.add(String(msg.id)));

              const existingMsgs = Array.from(messagesArea.querySelectorAll('.chat-message'));
              const tempMsgs = existingMsgs.filter(el => el.id && el.id.startsWith('temp-'));
              const currentOfficialIds = existingMsgs.filter(el => el.dataset.msgId && !el.dataset.msgId.toString().startsWith('temp-')).map(el => el.dataset.msgId).join(',');
              const newServerIds = messages.map(m => m.id).join(',');

              // Se nada mudou no servidor e não temos mensagens locais pendentes, não reconstrói o DOM
              if (currentOfficialIds === newServerIds && tempMsgs.length === 0 && messages.length > 0) return;

              // Limpa e reconstrói (estratégia simples para manter a ordem correta)
              const scrollTop = messagesArea.scrollTop;
              const isAtBottom = messagesArea.scrollHeight - messagesArea.scrollTop <= messagesArea.clientHeight + 50;

              messagesArea.innerHTML = '';
              messages.forEach(msg => appendMessageToUI(msg, false));
              
              // Re-insere mensagens locais (otimistas) que ainda não foram confirmadas pelo servidor
              const serverTexts = new Set(messages.filter(m => parseInt(m.senderId, 10) === currentUserId).map(m => m.message.trim()));
              tempMsgs.forEach(temp => {
                  const text = temp.querySelector('.message-text').textContent.trim();
                  if (!serverTexts.has(text)) {
                      messagesArea.appendChild(temp);
                  }
              });
              
              if (isAtBottom) {
                  messagesArea.scrollTop = messagesArea.scrollHeight;
              } else {
                  messagesArea.scrollTop = scrollTop;
              }
              if (incomingNewMessages.length > 0) {
                  const newestIncoming = incomingNewMessages[incomingNewMessages.length - 1];
                  if (String(newestIncoming.id) !== String(lastAlertedIncomingId)) {
                      lastAlertedIncomingId = newestIncoming.id;
                      if (window.ChatNotifier && typeof window.ChatNotifier.notifyIncomingInActiveChat === 'function') {
                          window.ChatNotifier.notifyIncomingInActiveChat({
                              id: newestIncoming.id,
                              from_name: document.querySelector('.conversation-title')?.textContent || 'Contato',
                              message: newestIncoming.message
                          });
                      }
                  }
              }
          })
          .catch(err => console.error('[CHAT] Erro polling mensagens:', err));
  }

  function sendMessage() {
      if (!selectedContactId) {
          if (typeof window.showAlert === 'function') window.showAlert('Selecione um contato primeiro.', 'warning');
          return;
      }
      
      const input = document.getElementById('messageInput');
      if (!input) return;
      const message = input.value.trim();
      if (!message) return;
      
      const tempId = 'temp-' + Date.now();
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
      .then(res => {
          if (!res.ok) throw new Error('Erro ao enviar: ' + res.status);
          return res.json();
      })
      .then(data => {
          if (!data.success) {
              const temp = document.getElementById(tempId);
              if (temp) temp.remove();
              if (typeof window.showAlert === 'function') window.showAlert(data.error || 'Erro ao enviar', 'danger');
          }
      })
      .catch(err => {
          console.error('[CHAT] Erro envio:', err);
          const temp = document.getElementById(tempId);
          if (temp) temp.remove();
          if (typeof window.showAlert === 'function') window.showAlert('Erro de conexão ao enviar mensagem.', 'danger');
      });
  }

  function markMessagesAsRead() {
      if (!selectedContactId || isNaN(selectedContactId)) return;
      fetch('/api/chat/mark_read', {
          method: 'POST',
          body: JSON.stringify({ from_user_id: selectedContactId })
      }).then(res => {
          if (res.ok) {
              if (typeof window.updateChatBadge === 'function') window.updateChatBadge();
              loadContacts();
          }
      }).catch(err => console.error('[CHAT] Erro marcar como lido:', err));
  }

  function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
  }

  // Inicialização
  document.addEventListener('DOMContentLoaded', () => {
      loadContacts();
      
      // Polling global
      setInterval(() => {
          if (selectedContactId) {
              loadMessages();
              markMessagesAsRead();
          } else {
              loadContacts();
          }
      }, 5000);
  });

  // Fallback caso DOMContentLoaded já tenha disparado
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
      loadContacts();
  }
  