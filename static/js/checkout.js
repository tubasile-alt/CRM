let currentPaymentId = null;

// Load checkouts when tab is clicked
document.addEventListener('DOMContentLoaded', function() {
    const checkoutTab = document.getElementById('checkout-tab');
    if (checkoutTab) {
        checkoutTab.addEventListener('click', loadCheckouts);
    }
});

function loadCheckouts() {
    fetch('/api/checkout/pending')
        .then(r => r.json())
        .then(result => {
            if (result.success) {
                displayCheckouts(result.checkouts);
            } else {
                showError(result.error || 'Erro ao carregar checkouts');
            }
        })
        .catch(err => console.error('Erro:', err));
}

function displayCheckouts(checkouts) {
    const container = document.getElementById('checkoutList');
    
    if (!checkouts || checkouts.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-success text-center">
                    <i class="bi bi-check-circle"></i> Nenhum checkout pendente
                </div>
            </div>
        `;
        return;
    }
    
    let html = '';
    checkouts.forEach(checkout => {
        const proceduresList = (checkout.procedures || [])
            .map(p => `<li>${p.name || 'Procedimento'} - R$ ${parseFloat(p.value || 0).toFixed(2)}</li>`)
            .join('');
        
        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100 shadow-sm">
                    <div class="card-header bg-primary text-white">
                        <h6 class="card-title mb-0">
                            <i class="bi bi-person"></i> ${checkout.patient_name}
                        </h6>
                    </div>
                    <div class="card-body">
                        <p class="text-muted mb-2">
                            <small><i class="bi bi-clock"></i> ${checkout.created_at}</small>
                        </p>
                        <p class="mb-3">
                            <strong>Tipo:</strong> ${checkout.consultation_type}
                        </p>
                        ${proceduresList ? `<strong>Procedimentos:</strong><ul class="small">${proceduresList}</ul>` : ''}
                    </div>
                    <div class="card-footer bg-light">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <strong class="text-success fs-5">R$ ${parseFloat(checkout.total_amount).toFixed(2)}</strong>
                            <span class="badge bg-warning">Pendente</span>
                        </div>
                        <button class="btn btn-success btn-sm w-100" onclick="openPaymentModal(${checkout.id}, '${checkout.patient_name}', ${checkout.total_amount})">
                            <i class="bi bi-credit-card"></i> Registrar Pagamento
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function openPaymentModal(paymentId, patientName, amount) {
    currentPaymentId = paymentId;
    document.getElementById('patientNamePayment').textContent = patientName;
    document.getElementById('paymentAmount').textContent = 'R$ ' + parseFloat(amount).toFixed(2);
    document.getElementById('paymentMethod').value = '';
    document.getElementById('installments').value = '1';
    document.getElementById('installmentsDiv').style.display = 'none';
    
    new bootstrap.Modal(document.getElementById('paymentModal')).show();
}

function updateInstallments() {
    const method = document.getElementById('paymentMethod').value;
    const div = document.getElementById('installmentsDiv');
    div.style.display = method === 'cartao' ? 'block' : 'none';
}

function completePayment() {
    const method = document.getElementById('paymentMethod').value;
    if (!method) {
        showError('Selecione uma forma de pagamento');
        return;
    }
    
    const installments = document.getElementById('installments').value;
    
    fetch(`/api/checkout/${currentPaymentId}/pay`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            payment_method: method,
            installments: parseInt(installments)
        })
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showSuccess('Pagamento registrado com sucesso!');
            bootstrap.Modal.getInstance(document.getElementById('paymentModal')).hide();
            loadCheckouts();
        } else {
            showError(result.error || 'Erro ao registrar pagamento');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showError('Erro ao processar pagamento');
    });
}
