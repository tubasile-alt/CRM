(function () {
    const ENABLE_BUTTON_ID = 'enable-push-notifications';
    const TEST_BUTTON_ID = 'test-push-notification';
    const PUBLIC_KEY_URL = '/api/push/vapid-public-key';
    const SUBSCRIBE_URL = '/api/push/subscribe';
    const STATUS_URL = '/api/push/status';
    const TEST_URL = '/api/push/test';

    // Compatibilidade iPhone/PWA: Web Push no iPhone exige iOS 16.4+, CRM adicionado
    // à Tela de Início, permissão de notificações concedida e HTTPS no ambiente.
    function isPushSupported() {
        return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
    }

    function isStandalonePwa() {
        return window.matchMedia('(display-mode: standalone)').matches
            || window.navigator.standalone === true;
    }

    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    async function readJsonResponse(response, fallbackMessage) {
        const contentType = response.headers.get('content-type') || '';
        let data = null;

        if (contentType.includes('application/json')) {
            data = await response.json();
        }

        if (response.redirected || (response.ok && !data)) {
            throw new Error('Sua sessão expirou. Entre novamente no CRM e tente de novo.');
        }
        if (!response.ok) {
            const error = new Error(data?.error || fallbackMessage);
            error.code = data?.code || null;
            error.status = response.status;
            throw error;
        }

        return data;
    }

    async function fetchJson(url, options = {}, fallbackMessage = 'Falha na comunicação com o servidor.') {
        const method = (options.method || 'GET').toUpperCase();
        const headers = { ...(options.headers || {}) };
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
            headers['X-CSRFToken'] = getCsrfToken();
        }

        const response = await fetch(url, {
            credentials: 'same-origin',
            ...options,
            headers,
        });
        return readJsonResponse(response, fallbackMessage);
    }

    function friendlyPushError(error) {
        if (!isStandalonePwa()) {
            return 'Abra o CRM pelo ícone adicionado à Tela de Início e tente novamente.';
        }
        if (error?.name === 'NotAllowedError') {
            return 'A permissão de notificações está bloqueada nos Ajustes do iPhone.';
        }
        if (error?.name === 'AbortError') {
            return 'O iPhone interrompeu a criação da notificação. Feche e abra a PWA e tente novamente.';
        }
        if (error?.name === 'InvalidAccessError' || error?.name === 'InvalidStateError') {
            return 'A chave pública VAPID é inválida ou mudou. A subscription precisa ser renovada.';
        }
        return error?.message || 'Não foi possível ativar as notificações push.';
    }

    function urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; i += 1) {
            outputArray[i] = rawData.charCodeAt(i);
        }

        return outputArray;
    }

    function setButtonState(buttonId, message, disabled = false) {
        const button = document.getElementById(buttonId);
        if (!button) return;
        button.disabled = disabled;
        button.textContent = message;
    }

    function setTestButtonState(message, disabled = false) {
        setButtonState(TEST_BUTTON_ID, message, disabled);
    }

    async function registerServiceWorker() {
        const registration = await navigator.serviceWorker.register('/service-worker.js', {
            scope: '/',
            updateViaCache: 'none',
        });
        registration.update().catch(() => undefined);
        return navigator.serviceWorker.ready;
    }

    async function getVapidPublicKey() {
        const data = await fetchJson(
            PUBLIC_KEY_URL,
            {},
            'Não foi possível obter a chave pública VAPID.'
        );
        if (!data?.publicKey) {
            throw new Error('A chave pública VAPID não está configurada no servidor.');
        }
        return data.publicKey;
    }

    async function saveSubscription(subscription) {
        return fetchJson(SUBSCRIBE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(subscription.toJSON()),
        }, 'Não foi possível salvar a subscription push.');
    }

    async function getPushStatus() {
        return fetchJson(STATUS_URL, {}, 'Não foi possível obter status das notificações.');
    }

    function applicationServerKeysMatch(subscription, expectedKey) {
        const currentKey = subscription?.options?.applicationServerKey;
        if (!currentKey) return true;

        const currentBytes = new Uint8Array(currentKey);
        if (currentBytes.length !== expectedKey.length) return false;
        return currentBytes.every((value, index) => value === expectedKey[index]);
    }

    async function syncPushSubscription() {
        const registration = await registerServiceWorker();
        const publicKey = await getVapidPublicKey();
        const applicationServerKey = urlBase64ToUint8Array(publicKey);
        if (applicationServerKey.length !== 65 || applicationServerKey[0] !== 4) {
            throw new DOMException('Chave pública VAPID inválida.', 'InvalidAccessError');
        }

        let subscription = await registration.pushManager.getSubscription();
        if (subscription && !applicationServerKeysMatch(subscription, applicationServerKey)) {
            await subscription.unsubscribe();
            subscription = null;
        }
        if (!subscription) {
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey,
            });
        }

        const data = await saveSubscription(subscription);
        setButtonState(ENABLE_BUTTON_ID, 'Sincronizar neste iPhone', false);
        setTestButtonState('Enviar notificação de teste', false);
        return data;
    }

    async function enablePushNotifications() {
        if (!isPushSupported()) {
            setButtonState(ENABLE_BUTTON_ID, 'Push indisponível neste dispositivo', true);
            setTestButtonState('Teste indisponível', true);
            return;
        }

        setButtonState(ENABLE_BUTTON_ID, 'Ativando notificações...', true);

        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            setButtonState(ENABLE_BUTTON_ID, 'Permissão de notificações negada', true);
            setTestButtonState('Teste indisponível', true);
            return;
        }

        await syncPushSubscription();
        setButtonState(ENABLE_BUTTON_ID, 'Sincronizar neste iPhone', false);
    }

    async function testPushNotifications() {
        if (!isPushSupported() || Notification.permission !== 'granted') {
            setTestButtonState('Ative as notificações primeiro', true);
            return;
        }

        setTestButtonState('Enviando teste...', true);
        const data = await fetchJson(TEST_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        }, 'Não foi possível enviar notificação de teste.');
        const result = data.result || {};
        if (window.showAlert) {
            const type = result.sent > 0 ? 'success' : 'warning';
            window.showAlert(`Teste push: ${result.sent || 0} enviada(s), ${result.failed || 0} falha(s).`, type);
        }
        setTestButtonState('Enviar notificação de teste', false);
        return data;
    }

    async function initializePushNotifications() {
        const button = document.getElementById(ENABLE_BUTTON_ID);
        const testButton = document.getElementById(TEST_BUTTON_ID);
        if (!button) {
            console.warn('[Push] Botão de ativar notificações NÃO encontrado no DOM');
            return;
        }
        console.log('[Push] Botão encontrado. isPushSupported:', isPushSupported());
        console.log('[Push] ServiceWorker:', 'serviceWorker' in navigator);
        console.log('[Push] PushManager:', 'PushManager' in window);
        console.log('[Push] Notification:', 'Notification' in window);
        console.log('[Push] Notification.permission:', 'Notification' in window ? Notification.permission : 'indisponível');

        if (!isPushSupported()) {
            console.warn('[Push] Push não suportado neste dispositivo');
            setButtonState(ENABLE_BUTTON_ID, 'Push indisponível neste dispositivo', true);
            setTestButtonState('Teste indisponível', true);
            return;
        }

        try {
            const reg = await registerServiceWorker();
            console.log('[Push] Service Worker registrado:', reg.scope);
        } catch (error) {
            console.error('[Push] Erro ao registrar service worker:', error);
            setButtonState(ENABLE_BUTTON_ID, 'Erro no service worker', true);
            setTestButtonState('Teste indisponível', true);
            return;
        }

        if (Notification.permission === 'granted') {
            setButtonState(ENABLE_BUTTON_ID, 'Sincronizando neste iPhone...', true);
            setTestButtonState('Preparando teste...', true);
            try {
                await syncPushSubscription();
                const status = await getPushStatus();
                if (status.has_subscription) {
                    setButtonState(ENABLE_BUTTON_ID, 'Sincronizar neste iPhone', false);
                    setTestButtonState('Enviar notificação de teste', false);
                }
            } catch (error) {
                console.error('[Push] Erro ao sincronizar subscription já permitida:', error);
                setButtonState(ENABLE_BUTTON_ID, 'Tentar sincronizar novamente', false);
                setTestButtonState('Teste indisponível', true);
            }
        } else if (Notification.permission === 'denied') {
            console.warn('[Push] Permissão BLOQUEADA pelo usuário');
            setButtonState(ENABLE_BUTTON_ID, 'Permissão bloqueada — desbloqueie nas configurações', true);
            setTestButtonState('Teste indisponível', true);
        } else {
            console.log('[Push] Permissão padrão (default), pronto para solicitar');
            setButtonState(ENABLE_BUTTON_ID, 'Ativar notificações neste iPhone', false);
            setTestButtonState('Enviar notificação de teste', true);
        }

        button.addEventListener('click', async () => {
            console.log('[Push] Botão clicado!');
            try {
                if (Notification.permission === 'granted') {
                    setButtonState(ENABLE_BUTTON_ID, 'Sincronizando neste iPhone...', true);
                    await syncPushSubscription();
                } else {
                    await enablePushNotifications();
                }
            } catch (error) {
                console.error('[Push] Erro ao ativar notificações:', error);
                setButtonState(ENABLE_BUTTON_ID, 'Tentar ativar/sincronizar novamente', false);
                if (window.showAlert) {
                    window.showAlert(friendlyPushError(error), 'warning');
                }
            }
        });

        if (testButton) {
            testButton.addEventListener('click', async () => {
                try {
                    await testPushNotifications();
                } catch (error) {
                    console.error('[Push] Erro no teste push:', error);
                    setTestButtonState('Tentar teste novamente', false);
                    if (window.showAlert) {
                        window.showAlert(friendlyPushError(error), 'warning');
                    }
                }
            });
        }
    }

    window.enablePushNotifications = enablePushNotifications;
    window.testPushNotifications = testPushNotifications;
    document.addEventListener('DOMContentLoaded', initializePushNotifications);
}());
