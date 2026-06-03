const DEFAULT_TITLE = 'Paciente chegou';
const DEFAULT_ICON = '/icon-192.png';
const DEFAULT_BADGE = '/icon-192.png';

self.addEventListener('push', (event) => {
    let payload = {};

    if (event.data) {
        try {
            payload = event.data.json();
        } catch (error) {
            payload = { body: event.data.text() };
        }
    }

    const title = payload.title || DEFAULT_TITLE;
    const options = {
        body: payload.body || 'Um paciente fez check-in',
        icon: payload.icon || DEFAULT_ICON,
        badge: payload.badge || DEFAULT_BADGE,
        data: payload.data || {},
        requireInteraction: true,
        tag: payload.data?.appointment_id ? `checkin-${payload.data.appointment_id}` : 'checkin',
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    const targetUrl = new URL(event.notification.data?.url || '/', self.location.origin).href;

    event.waitUntil((async () => {
        const windowClients = await clients.matchAll({ type: 'window', includeUncontrolled: true });

        for (const client of windowClients) {
            if ('focus' in client && new URL(client.url).origin === self.location.origin) {
                if ('navigate' in client) {
                    await client.navigate(targetUrl);
                }
                return client.focus();
            }
        }

        if (clients.openWindow) {
            return clients.openWindow(targetUrl);
        }

        return undefined;
    })());
});
