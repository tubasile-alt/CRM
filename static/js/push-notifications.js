(function () {
    const ENABLE_BUTTON_ID = 'enable-push-notifications';
    const PUBLIC_KEY_URL = '/api/push/vapid-public-key';
    const SUBSCRIBE_URL = '/api/push/subscribe';

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

    function setButtonState(message, disabled = false) {
        const button = document.getElementById(ENABLE_BUTTON_ID);
        if (!button) return;
        button.disabled = disabled;
        button.textContent = message;
    }

    async function registerServiceWorker() {
        return navigator.serviceWorker.register('/service-worker.js', { scope: '/' });
    }

    async function getVapidPublicKey() {
        const response = await fetch(PUBLIC_KEY_URL);
        if (!response.ok) {
            throw new Error('Não foi possível obter a chave pública VAPID.');
        }
        const data = await response.json();
        return data.publicKey;
    }

    async function saveSubscription(subscription) {
        const response = await fetch(SUBSCRIBE_URL, {
            method: 'POST',
            body: JSON.stringify(subscription.toJSON()),
        });

        if (!response.ok) {
            throw new Error('Não foi possível salvar a subscription push.');
        }

        return response.json();
    }

    async function enablePushNotifications() {
        if (!isPushSupported()) {
            setButtonState('Push indisponível neste dispositivo', true);
            return;
        }

        setButtonState('Ativando notificações...', true);

        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            setButtonState('Permissão de notificações negada', true);
            return;
        }

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

        await saveSubscription(subscription);
        setButtonState('Notificações ativadas neste iPhone', true);
    }

    async function initializePushNotifications() {
        const button = document.getElementById(ENABLE_BUTTON_ID);
        if (!button) return;

        if (!isPushSupported()) {
            setButtonState('Push indisponível neste dispositivo', true);
            return;
        }

        try {
            await registerServiceWorker();
            if (Notification.permission === 'granted') {
                setButtonState('Notificações já permitidas', false);
            }
        } catch (error) {
            console.error('[Push] Erro ao registrar service worker:', error);
        }

        button.addEventListener('click', async () => {
            try {
                await enablePushNotifications();
            } catch (error) {
                console.error('[Push] Erro ao ativar notificações:', error);
                setButtonState('Tentar ativar notificações novamente', false);
                if (window.showAlert) {
                    window.showAlert('Erro ao ativar notificações push. Verifique HTTPS, PWA na Tela de Início e chaves VAPID.', 'warning');
                }
            }
        });
    }

    window.enablePushNotifications = enablePushNotifications;
    document.addEventListener('DOMContentLoaded', initializePushNotifications);
}());
