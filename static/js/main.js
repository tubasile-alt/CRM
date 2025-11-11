const originalFetch = window.fetch;

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

window.getCSRFToken = getCsrfToken;

function fetchWithCsrf(url, options = {}) {
    if (!options.headers) {
        options.headers = {};
    }
    
    if (options.method && options.method !== 'GET') {
        options.headers['X-CSRFToken'] = getCsrfToken();
    }
    
    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
    }
    
    return originalFetch(url, options);
}

window.fetch = fetchWithCsrf;

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
