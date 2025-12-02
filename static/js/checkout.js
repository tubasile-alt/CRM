let currentPaymentId = null;
let currentCheckoutData = null;

document.addEventListener('DOMContentLoaded', function() {
    const checkoutTab = document.getElementById('checkout-tab');
    if (checkoutTab) {
        checkoutTab.addEventListener('click', loadCheckouts);
    }
    
    updatePendingCheckoutBadge();
    setInterval(updatePendingCheckoutBadge, 30000);
});

function updatePendingCheckoutBadge() {
    fetch('/api/checkout/pending/count')
        .then(r => r.json())
        .then(result => {
            if (result.success) {
                const badge = document.getElementById('pendingCheckoutBadge');
                if (badge) {
                    if (result.count > 0) {
                        badge.textContent = result.count;
                        badge.style.display = 'inline-block';
                    } else {
                        badge.style.display = 'none';
                    }
                }
            }
        })
        .catch(err => console.error('Erro ao buscar contagem:', err));
}

function loadCheckouts() {
    fetch('/api/checkout/pending')
        .then(r => r.json())
        .then(result => {
            if (result.success) {
                displayCheckouts(result.checkouts);
                updatePendingCheckoutBadge();
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
    
    const pending = checkouts.filter(c => c.status === 'pendente');
    const paid = checkouts.filter(c => c.status === 'pago');
    
    let html = '';
    
    if (pending.length > 0) {
        html += '<div class="row mb-3"><div class="col-12"><h5 class="text-warning"><i class="bi bi-hourglass-split"></i> Pendentes</h5></div></div>';
        pending.forEach(checkout => {
            html += createCheckoutCard(checkout);
        });
    }
    
    if (paid.length > 0) {
        html += '<div class="row mb-3"><div class="col-12"><h5 class="text-success"><i class="bi bi-check-circle"></i> Realizados</h5></div></div>';
        paid.forEach(checkout => {
            html += createCheckoutCard(checkout);
        });
    }
    
    container.innerHTML = html;
}

function createCheckoutCard(checkout) {
    const isPaid = checkout.status === 'pago';
    const badgeClass = isPaid ? 'bg-success' : 'bg-warning';
    const badgeText = isPaid ? 'Realizado' : 'Pendente';
    const paymentMethodText = isPaid ? `<small class="text-muted ms-2">${checkout.payment_method}</small>` : '';
    const paidAtText = isPaid ? `<p class="text-muted mb-2"><small><i class="bi bi-check-lg"></i> Pago às ${checkout.paid_at}</small></p>` : '';
    
    const procedures = checkout.procedures || [];
    const consultationItem = procedures.find(p => (p.name || '').startsWith('Consulta'));
    const otherProcedures = procedures.filter(p => !(p.name || '').startsWith('Consulta'));
    
    const computedTotal = procedures.reduce((sum, p) => sum + parseFloat(p.value || 0), 0);
    
    let itemsHtml = '<table class="table table-sm table-borderless mb-2" style="font-size: 0.85rem;">';
    
    if (consultationItem) {
        const checkboxId = `charge-consult-${checkout.id}`;
        itemsHtml += `
            <tr class="border-bottom">
                <td style="width: 30px;">
                    ${!isPaid ? `<input type="checkbox" class="form-check-input" id="${checkboxId}" 
                        onchange="toggleConsultationCharge(${checkout.id}, this.checked)" 
                        checked>` : '<i class="bi bi-check text-success"></i>'}
                </td>
                <td><strong>${consultationItem.name}</strong></td>
                <td class="text-end text-primary"><strong>R$ ${parseFloat(consultationItem.value || 0).toFixed(2)}</strong></td>
            </tr>
        `;
    } else if (!isPaid) {
        const consultationType = checkout.consultation_type || 'Particular';
        const consultationValue = getConsultationPrice(consultationType);
        if (consultationValue > 0) {
            const checkboxId = `charge-consult-${checkout.id}`;
            itemsHtml += `
                <tr class="border-bottom text-muted">
                    <td style="width: 30px;">
                        <input type="checkbox" class="form-check-input" id="${checkboxId}" 
                            onchange="toggleConsultationCharge(${checkout.id}, this.checked)">
                    </td>
                    <td><span class="text-decoration-line-through">Consulta ${consultationType}</span></td>
                    <td class="text-end"><span class="text-decoration-line-through">R$ ${consultationValue.toFixed(2)}</span></td>
                </tr>
            `;
        }
    }
    
    if (otherProcedures.length > 0) {
        otherProcedures.forEach(proc => {
            itemsHtml += `
                <tr>
                    <td style="width: 30px;"><i class="bi bi-dot"></i></td>
                    <td>${proc.name || 'Procedimento'}</td>
                    <td class="text-end">R$ ${parseFloat(proc.value || 0).toFixed(2)}</td>
                </tr>
            `;
        });
    }
    
    if (procedures.length === 0 && !consultationItem) {
        itemsHtml += '<tr><td colspan="3" class="text-muted text-center"><em>Sem itens</em></td></tr>';
    }
    
    itemsHtml += '</table>';
    
    const buttonHtml = isPaid ? '' : `
        <button class="btn btn-success btn-sm w-100" onclick="openPaymentModal(${checkout.id}, '${checkout.patient_name.replace(/'/g, "\\'")}', ${computedTotal.toFixed(2)})">
            <i class="bi bi-credit-card"></i> Registrar Pagamento
        </button>
    `;
    
    return `
        <div class="col-md-6 col-lg-4 mb-4" id="checkout-card-${checkout.id}">
            <div class="card h-100 shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h6 class="card-title mb-0">
                        <i class="bi bi-person"></i> ${checkout.patient_name}
                    </h6>
                </div>
                <div class="card-body">
                    <p class="text-muted mb-2">
                        <small><i class="bi bi-clock"></i> ${checkout.created_at}</small>
                        <span class="badge bg-info ms-2">${checkout.consultation_type}</span>
                    </p>
                    <hr class="my-2">
                    <strong class="d-block mb-2">Itens:</strong>
                    ${itemsHtml}
                    ${paidAtText}
                </div>
                <div class="card-footer bg-light">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <strong class="text-success fs-5" id="total-${checkout.id}">R$ ${computedTotal.toFixed(2)}</strong>
                        <span class="badge ${badgeClass}">${badgeText}${paymentMethodText}</span>
                    </div>
                    ${buttonHtml}
                </div>
            </div>
        </div>
    `;
}

function getConsultationPrice(consultationType) {
    const prices = {
        'Particular': 400.0,
        'Transplante Capilar': 400.0,
        'Retorno': 0.0,
        'UNIMED': 0.0,
        'Cortesia': 0.0,
        'Consulta Cortesia': 0.0
    };
    return prices[consultationType] || 0.0;
}

function toggleConsultationCharge(paymentId, chargeConsultation) {
    fetch(`/api/checkout/${paymentId}/toggle-consultation`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            charge_consultation: chargeConsultation
        })
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            showAlert(result.message, 'success');
            loadCheckouts();
        } else {
            showAlert(result.error || 'Erro ao atualizar', 'danger');
            loadCheckouts();
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao atualizar cobrança', 'danger');
        loadCheckouts();
    });
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
            setTimeout(() => {
                loadCheckouts();
                updatePendingCheckoutBadge();
            }, 500);
        } else {
            showAlert(result.error || 'Erro ao registrar pagamento', 'danger');
        }
    })
    .catch(err => {
        console.error('Erro:', err);
        showAlert('Erro ao processar pagamento', 'danger');
    });
}
