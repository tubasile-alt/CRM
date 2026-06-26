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
        return navigator.serviceWorker.register('/service-worker.js', { scope: '/' });
    }

    async function getVapidPublicKey() {
        const response = await fetch(PUBLIC_KEY_URL, {
            credentials: 'same-origin',
        });
        if (!response.ok) {
            throw new Error('Não foi possível obter a chave pública VAPID.');
        }
        const data = await response.json();
        return data.publicKey;
    }

    async function saveSubscription(subscription) {
        const response = await fetch(SUBSCRIBE_URL, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(subscription.toJSON()),
        });

        if (!response.ok) {
            throw new Error('Não foi possível salvar a subscription push.');
        }

        return response.json();
    }

    async function getPushStatus() {
        const response = await fetch(STATUS_URL, {
            credentials: 'same-origin',
        });
        if (!response.ok) {
            throw new Error('Não foi possível obter status das notificações.');
        }
        return response.json();
    }

    async function syncPushSubscription() {
        const registration = await registerServiceWorker();
        const publicKey = await getVapidPublicKey();
        const applicationServerKey = urlBase64ToUint8Array(publicKey);

        let subscription = await registration.pushManager.getSubscription();
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
        const response = await fetch(TEST_URL, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        });
        if (!response.ok) {
            throw new Error('Não foi possível enviar notificação de teste.');
        }

        const data = await response.json();
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
                setButtonState(ENABLE_BUTTON_ID, 'Sincronizar neste iPhone', false);
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
                    window.showAlert('Erro ao ativar notificações push. Verifique HTTPS, PWA na Tela de Início e chaves VAPID.', 'warning');
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
                        window.showAlert('Erro ao enviar teste push. Sincronize este iPhone e tente novamente.', 'warning');
                    }
                }
            });
        }
    }

    window.enablePushNotifications = enablePushNotifications;
    window.testPushNotifications = testPushNotifications;
    document.addEventListener('DOMContentLoaded', initializePushNotifications);
}());
