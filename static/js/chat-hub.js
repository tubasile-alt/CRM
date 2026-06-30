(() => {
    'use strict';

    const fab = document.getElementById('chat-hub-fab');
    const drawerElement = document.getElementById('chat-hub-drawer');
    if (!fab || !drawerElement || !window.bootstrap) return;

    const drawer = bootstrap.Offcanvas.getOrCreateInstance(drawerElement);
    const contactsView = document.getElementById('chat-hub-contacts-view');
    const conversationView = document.getElementById('chat-hub-conversation-view');
    const contactsElement = document.getElementById('chat-hub-contacts');
    const messagesElement = document.getElementById('chat-hub-messages');
    const titleElement = document.getElementById('chat-hub-title');
    const subtitleElement = document.getElementById('chat-hub-subtitle');
    const backButton = document.getElementById('chat-hub-back');
    const form = document.getElementById('chat-hub-form');
    const input = document.getElementById('chat-hub-input');
    const sendButton = document.getElementById('chat-hub-send');
    const currentUserId = Number.parseInt(document.body.dataset.userId || '0', 10);

    let contacts = [];
    let selectedContact = null;
    let pollTimer = null;
    let requestSequence = 0;
    let contactsRequestSequence = 0;
    let pollingMessages = false;
    let pollingGeneration = 0;
    let lastMessagesSignature = '';

    function drawerIsOpen() {
        return drawerElement.classList.contains('show') || drawerElement.classList.contains('showing');
    }

    function initials(name) {
        return String(name || '?')
            .trim()
            .split(/\s+/)
            .slice(0, 2)
            .map(part => part.charAt(0).toUpperCase())
            .join('') || '?';
    }

    function setState(container, message, loading = false) {
        container.replaceChildren();
        const state = document.createElement('div');
        state.className = 'chat-hub-state';
        if (loading) {
            const spinner = document.createElement('span');
            spinner.className = 'spinner-border spinner-border-sm';
            spinner.setAttribute('aria-hidden', 'true');
            state.appendChild(spinner);
        }
        const text = document.createElement('span');
        text.textContent = message;
        state.appendChild(text);
        container.appendChild(state);
    }

    async function fetchJson(url, options) {
        const response = await fetch(url, options);
        const contentType = response.headers.get('content-type') || '';
        if (!response.ok || !contentType.includes('application/json')) {
            throw new Error(`Falha na comunicação (${response.status})`);
        }
        return response.json();
    }

    function renderContacts() {
        contactsElement.replaceChildren();
        if (!contacts.length) {
            setState(contactsElement, 'Nenhum contato disponível.');
            return;
        }

        const fragment = document.createDocumentFragment();
        contacts.forEach(contact => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'chat-hub-contact';
            button.dataset.contactId = String(contact.id);

            const avatar = document.createElement('span');
            avatar.className = 'chat-hub-avatar';
            avatar.textContent = initials(contact.name);
            avatar.setAttribute('aria-hidden', 'true');

            const copy = document.createElement('span');
            copy.className = 'chat-hub-contact-copy';
            const name = document.createElement('span');
            name.className = 'chat-hub-contact-name';
            name.textContent = contact.name;
            const role = document.createElement('span');
            role.className = 'chat-hub-contact-role';
            role.textContent = contact.role === 'medico' ? 'Médico' : 'Secretaria';
            copy.append(name, role);
            button.append(avatar, copy);

            const unread = Number(contact.unread_count || 0);
            if (unread > 0) {
                const badge = document.createElement('span');
                badge.className = 'chat-hub-contact-unread';
                badge.textContent = unread > 99 ? '99+' : String(unread);
                badge.setAttribute('aria-label', `${unread} mensagens não lidas`);
                button.appendChild(badge);
            }

            button.addEventListener('click', () => selectContact(contact));
            fragment.appendChild(button);
        });
        contactsElement.appendChild(fragment);
    }

    async function loadContacts(preferredContactId = null) {
        const sequence = ++contactsRequestSequence;
        setState(contactsElement, 'Carregando contatos...', true);
        try {
            const result = await fetchJson('/api/chat/contacts');
            if (sequence !== contactsRequestSequence || !drawerIsOpen()) return;
            contacts = Array.isArray(result) ? result : [];
            renderContacts();
            if (preferredContactId) {
                const preferred = contacts.find(contact => Number(contact.id) === Number(preferredContactId));
                if (preferred) await selectContact(preferred);
            }
        } catch (error) {
            if (sequence !== contactsRequestSequence || !drawerIsOpen()) return;
            console.error('[ChatHub] Erro ao carregar contatos:', error);
            setState(contactsElement, 'Não foi possível carregar os contatos. Tente novamente.');
        }
    }

    function showContacts() {
        selectedContact = null;
        contactsView.hidden = false;
        conversationView.hidden = true;
        backButton.hidden = true;
        titleElement.textContent = 'Conversas';
        subtitleElement.textContent = 'Comunicação interna da clínica';
        stopPolling();
        loadContacts();
    }

    function renderMessages(messages) {
        const signature = JSON.stringify(messages.map(message => [message.id, message.message, message.timestamp]));
        if (signature === lastMessagesSignature) return false;
        lastMessagesSignature = signature;
        const wasNearBottom = messagesElement.scrollHeight - messagesElement.scrollTop - messagesElement.clientHeight < 80;
        messagesElement.replaceChildren();
        if (!messages.length) {
            setState(messagesElement, 'Nenhuma mensagem nesta conversa.');
            return true;
        }

        const fragment = document.createDocumentFragment();
        messages.forEach(message => {
            const item = document.createElement('div');
            item.className = 'chat-hub-message';
            if (Number(message.senderId) === currentUserId) item.classList.add('is-sent');
            item.dataset.messageId = String(message.id);

            const text = document.createElement('div');
            text.textContent = message.message || '';
            const time = document.createElement('time');
            time.className = 'chat-hub-message-time';
            time.textContent = message.timestamp || '';
            item.append(text, time);
            fragment.appendChild(item);
        });
        messagesElement.appendChild(fragment);
        if (wasNearBottom || !messagesElement.dataset.loaded) {
            messagesElement.scrollTop = messagesElement.scrollHeight;
        }
        messagesElement.dataset.loaded = 'true';
        return true;
    }

    async function markConversationRead(contactId) {
        try {
            await fetchJson('/api/chat/mark_read', {
                method: 'POST',
                body: JSON.stringify({ from_user_id: contactId })
            });
            window.updateChatBadge?.();
        } catch (error) {
            console.error('[ChatHub] Erro ao marcar mensagens como lidas:', error);
        }
    }

    async function loadMessages({ markRead = false, quiet = false } = {}) {
        if (!selectedContact) return;
        const contactId = selectedContact.id;
        const sequence = ++requestSequence;
        if (!quiet) setState(messagesElement, 'Carregando conversa...', true);

        try {
            const result = await fetchJson(`/api/chat/messages?with_user_id=${encodeURIComponent(contactId)}&t=${Date.now()}`);
            if (sequence !== requestSequence || !selectedContact || Number(selectedContact.id) !== Number(contactId)) return;
            const messagesChanged = renderMessages(Array.isArray(result) ? result : []);
            if (markRead && messagesChanged) await markConversationRead(contactId);
        } catch (error) {
            console.error('[ChatHub] Erro ao carregar mensagens:', error);
            if (!quiet) setState(messagesElement, 'Não foi possível carregar a conversa.');
        }
    }

    async function selectContact(contact) {
        const contactId = Number(contact.id);
        selectedContact = contact;
        lastMessagesSignature = '';
        delete messagesElement.dataset.loaded;
        contactsView.hidden = true;
        conversationView.hidden = false;
        backButton.hidden = false;
        titleElement.textContent = contact.name;
        subtitleElement.textContent = contact.role === 'medico' ? 'Médico' : 'Secretaria';
        await loadMessages({ markRead: true });
        if (!selectedContact || Number(selectedContact.id) !== contactId || !drawerIsOpen()) return;
        startPolling();
        input.focus({ preventScroll: true });
    }

    function startPolling() {
        stopPolling();
        pollTimer = window.setInterval(() => {
            if (!document.hidden && drawerIsOpen() && selectedContact && !pollingMessages) {
                pollingMessages = true;
                const generation = ++pollingGeneration;
                loadMessages({ markRead: true, quiet: true })
                    .finally(() => {
                        if (generation === pollingGeneration) pollingMessages = false;
                    });
            }
        }, 5000);
    }

    function stopPolling() {
        if (pollTimer) window.clearInterval(pollTimer);
        pollTimer = null;
        pollingGeneration += 1;
        pollingMessages = false;
    }

    async function sendMessage(event) {
        event.preventDefault();
        event.stopPropagation();
        if (!selectedContact || sendButton.disabled) return;

        const message = input.value.trim();
        if (!message) return;

        sendButton.disabled = true;
        try {
            const result = await fetchJson('/api/chat/send', {
                method: 'POST',
                body: JSON.stringify({ recipient_id: selectedContact.id, message })
            });
            if (!result.success) throw new Error(result.error || 'Falha ao enviar');
            input.value = '';
            input.style.height = '';
            await loadMessages({ quiet: true });
            input.focus({ preventScroll: true });
        } catch (error) {
            console.error('[ChatHub] Erro ao enviar mensagem:', error);
            window.showAlert?.('Não foi possível enviar a mensagem. Tente novamente.', 'danger');
        } finally {
            sendButton.disabled = false;
        }
    }

    function open(preferredContactId = null) {
        drawer.show();
        loadContacts(preferredContactId);
    }

    fab.addEventListener('click', () => open());
    backButton.addEventListener('click', showContacts);
    form.addEventListener('submit', sendMessage);
    input.addEventListener('keydown', event => {
        if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
            sendMessage(event);
        }
    });
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = `${Math.min(input.scrollHeight, 112)}px`;
    });
    drawerElement.addEventListener('hidden.bs.offcanvas', () => {
        stopPolling();
        contactsRequestSequence += 1;
        selectedContact = null;
        lastMessagesSignature = '';
        requestSequence += 1;
        contactsView.hidden = false;
        conversationView.hidden = true;
        backButton.hidden = true;
        titleElement.textContent = 'Conversas';
        subtitleElement.textContent = 'Comunicação interna da clínica';
    });
    document.addEventListener('keydown', event => {
        if (event.altKey && event.key.toLowerCase() === 'n') {
            event.preventDefault();
            open();
        }
    });

    window.ChatHub = { open };
})();
