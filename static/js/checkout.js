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
                showAlert(result.error || 'Erro ao carregar checkouts', 'danger');
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
                    <i class="bi bi-check-circle"></i> Nenhum checkout para hoje
                </div>
            </div>
        `;
        return;
    }
    
    // Separar pendentes e pagos
    const pending = checkouts.filter(c => c.status === 'pendente');
    const paid = checkouts.filter(c => c.status === 'pago');
    
    let html = '';
    
    // Mostrar pendentes primeiro
    if (pending.length > 0) {
        html += '<div class="row mb-3"><div class="col-12"><h5 class="text-warning"><i class="bi bi-hourglass-split"></i> Pendentes</h5></div></div>';
        pending.forEach(checkout => {
            html += createCheckoutCard(checkout);
        });
    }
    
    // Mostrar pagos depois
    if (paid.length > 0) {
        html += '<div class="row mb-3"><div class="col-12"><h5 class="text-success"><i class="bi bi-check-circle"></i> Realizados</h5></div></div>';
        paid.forEach(checkout => {
            html += createCheckoutCard(checkout);
        });
    }
    
    container.innerHTML = html;
}

function createCheckoutCard(checkout) {
    const proceduresList = (checkout.procedures || [])
        .map(p => `<li>${p.name || 'Procedimento'} - R$ ${parseFloat(p.value || 0).toFixed(2)}</li>`)
        .join('');
    
    const isPaid = checkout.status === 'pago';
    const badgeClass = isPaid ? 'bg-success' : 'bg-warning';
    const badgeText = isPaid ? 'Realizado' : 'Pendente';
    const paymentMethodText = isPaid ? `<small class="text-muted ms-2">${checkout.payment_method}</small>` : '';
    const paidAtText = isPaid ? `<p class="text-muted mb-2"><small><i class="bi bi-check-lg"></i> Pago às ${checkout.paid_at}</small></p>` : '';
    const buttonHtml = isPaid ? '' : `
        <button class="btn btn-success btn-sm w-100" onclick="openPaymentModal(${checkout.id}, '${checkout.patient_name}', ${checkout.total_amount})">
            <i class="bi bi-credit-card"></i> Registrar Pagamento
        </button>
    `;
    
    return `
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
                    ${paidAtText}
                </div>
                <div class="card-footer bg-light">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <strong class="text-success fs-5">R$ ${parseFloat(checkout.total_amount).toFixed(2)}</strong>
                        <span class="badge ${badgeClass}">${badgeText}${paymentMethodText}</span>
                    </div>
                    ${buttonHtml}
                </div>
            </div>
        </div>
    `;
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
        showAlert('Selecione uma forma de pagamento', 'danger');
        return;
    }
    
    const installments = document.getElementById('installments').value;
    
    fetch(`/api/checkout/${currentPaymentId}/pay`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            payment_method: method,
            installments: parseInt(installments)
        })
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert('Pagamento registrado com sucesso!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('paymentModal')).hide();
            setTimeout(loadCheckouts, 500);
        } else {
            showAlert(result.error || 'Erro ao registrar pagamento', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao processar pagamento', 'danger');
    });
}
