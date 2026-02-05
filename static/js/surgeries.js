// ========== GERENCIAR CIRURGIAS ==========

// Tornar as funcoes globais anexando ao objeto window explicitamente
window.saveSurgery = function() {
    console.log('saveSurgery chamada');
    
    // Tentar pegar patientId de varias fontes
    var pId = typeof patientId !== 'undefined' ? patientId : null;
    if (!pId) {
        var el = document.getElementById('detailPatientId');
        if (el) pId = el.value;
    }
    
    if (!pId) {
        console.error('patientId nao encontrado!');
        if (typeof showAlert === 'function') {
            showAlert('Erro: ID do paciente nao encontrado.', 'danger');
        } else {
            alert('Erro: ID do paciente nao encontrado.');
        }
        return;
    }

    // IDs dos campos podem variar entre a aba "Cirurgias" e o modal de "Planejamento"
    var surgeryDateEl = document.getElementById('surgeryDate');
    var surgeryModalDateEl = document.getElementById('surgeryModalDate');
    var surgeryDate = (surgeryDateEl && surgeryDateEl.value) || (surgeryModalDateEl && surgeryModalDateEl.value) || '';
    
    var surgicalDataEl = document.getElementById('surgicalData');
    var surgeryModalPlanningEl = document.getElementById('surgeryModalSurgicalPlanning');
    var surgicalData = ((surgicalDataEl && surgicalDataEl.value) || (surgeryModalPlanningEl && surgeryModalPlanningEl.value) || '').trim();
    
    var observationsEl = document.getElementById('surgeryObservations');
    var surgeryModalCompEl = document.getElementById('surgeryModalComplications');
    var observations = ((observationsEl && observationsEl.value) || (surgeryModalCompEl && surgeryModalCompEl.value) || '').trim();
    
    // Coletar tipos de cirurgia selecionados
    var surgeryTypes = [];
    var typeCheckboxes = ['surgeryTypeCapilar', 'surgeryTypeBodyHair', 'surgeryTypeSobrancelhas', 'surgeryTypeBarba', 'surgeryTypeRetoque'];
    typeCheckboxes.forEach(function(id) {
        var cb = document.getElementById(id);
        if (cb && cb.checked) {
            surgeryTypes.push(cb.value);
        }
    });
    var surgeryType = surgeryTypes.join(', ');
    
    if (!surgeryDate) {
        if (typeof showAlert === 'function') showAlert('Selecione a data da cirurgia!', 'warning');
        return;
    }
    
    if (!surgicalData) {
        if (typeof showAlert === 'function') showAlert('Preencha os dados cirurgicos!', 'warning');
        return;
    }
    
    fetch('/api/patient/' + pId + '/surgery', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', 
            'X-CSRFToken': typeof getCSRFToken === 'function' ? getCSRFToken() : ''
        },
        body: JSON.stringify({
            surgery_date: surgeryDate.split('T')[0],
            surgical_data: surgicalData,
            observations: observations,
            surgery_type: surgeryType
        })
    })
    .then(function(r) {
        if (!r.ok) throw new Error('Servidor retornou erro');
        return r.json();
    })
    .then(function(result) {
        if (result.success) {
            if (typeof showAlert === 'function') showAlert('Cirurgia registrada com sucesso!', 'success');
            // Limpar campos de ambos os formularios
            var ids = ['surgeryDate', 'surgicalData', 'surgeryObservations', 'surgeryModalDate', 'surgeryModalSurgicalPlanning', 'surgeryModalComplications'];
            ids.forEach(function(id) {
                var el = document.getElementById(id);
                if (el) el.value = '';
            });
            // Limpar checkboxes de tipo de cirurgia
            ['surgeryTypeCapilar', 'surgeryTypeBodyHair', 'surgeryTypeSobrancelhas', 'surgeryTypeBarba', 'surgeryTypeRetoque'].forEach(function(id) {
                var cb = document.getElementById(id);
                if (cb) cb.checked = false;
            });
            
            // Fechar modal se aberto
            var modalEl = document.getElementById('surgeryModal');
            if (modalEl && typeof bootstrap !== 'undefined') {
                var modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }
            
            if (typeof window.loadSurgeries === 'function') window.loadSurgeries();
        } else {
            if (typeof showAlert === 'function') showAlert('Erro: ' + (result.error || 'Erro ao salvar'), 'danger');
        }
    })
    .catch(function(err) {
        console.error('Erro:', err);
        if (typeof showAlert === 'function') showAlert('Erro ao salvar cirurgia', 'danger');
    });
};

window.loadSurgeries = function() {
    console.log('loadSurgeries chamada');
    var pId = typeof patientId !== 'undefined' ? patientId : null;
    if (!pId) {
        var el = document.getElementById('detailPatientId');
        if (el) pId = el.value;
    }
    if (!pId) {
        console.warn('loadSurgeries: pId nao encontrado');
        return;
    }
    
    fetch('/api/patient/' + pId + '/surgeries')
        .then(function(r) {
            if (!r.ok) throw new Error('Servidor retornou erro');
            return r.json();
        })
        .then(function(surgeries) {
            console.log('Cirurgias carregadas:', surgeries);
            renderSurgeries(surgeries);
        })
        .catch(function(err) { 
            console.error('Erro ao carregar cirurgias:', err); 
        });
};

window.deleteSurgery = function(surgeryId) {
    if (!confirm('Tem certeza que deseja deletar esta cirurgia?')) return;
    
    console.log('Deletando cirurgia ID:', surgeryId);
    
    var id = parseInt(surgeryId);
    if (isNaN(id)) {
        console.error('ID invalido para delecao:', surgeryId);
        return;
    }
    
    fetch('/api/patient/delete/' + id, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': typeof getCSRFToken === 'function' ? getCSRFToken() : ''
        }
    })
    .then(function(r) {
        if (!r.ok) {
            console.error('Erro na resposta do servidor:', r.status);
            throw new Error('Falha na resposta do servidor');
        }
        return r.json();
    })
    .then(function(result) {
        console.log('Resultado delecao:', result);
        if (result.success) {
            if (typeof showAlert === 'function') showAlert('Cirurgia deletada!', 'success');
            if (typeof window.loadSurgeries === 'function') window.loadSurgeries();
        } else {
            console.error('Erro retornado pelo servidor:', result.error);
            if (typeof showAlert === 'function') showAlert('Erro: ' + (result.error || 'Erro ao deletar'), 'danger');
        }
    })
    .catch(function(err) {
        console.error('Erro ao deletar cirurgia:', err);
        if (typeof showAlert === 'function') showAlert('Erro ao deletar cirurgia', 'danger');
    });
};

function calculateSurgeryTime(surgeryDate) {
    try {
        var dateStr = surgeryDate;
        if (surgeryDate.indexOf('/') !== -1) {
            var parts = surgeryDate.split('/');
            dateStr = parts[2] + '-' + parts[1] + '-' + parts[0];
        }
        
        var dateParts = dateStr.split('-').map(Number);
        var year = dateParts[0];
        var month = dateParts[1];
        var day = dateParts[2];
        var surgery = new Date(Date.UTC(year, month - 1, day));
        var today = new Date();
        
        var years = today.getFullYear() - surgery.getFullYear();
        var months = today.getMonth() - surgery.getMonth();
        var days = today.getDate() - surgery.getDate();
        
        if (days < 0) {
            months--;
            days += 30;
        }
        if (months < 0) {
            years--;
            months += 12;
        }
        
        var dayStr = day.toString().padStart(2, '0');
        var monthStr = month.toString().padStart(2, '0');
        var timeStr = dayStr + '/' + monthStr + '/' + year;
        var timePassed = [];
        
        if (years > 0) timePassed.push(years + ' ano' + (years > 1 ? 's' : ''));
        if (months > 0) timePassed.push(months + ' mes' + (months > 1 ? 'es' : ''));
        if (days > 0 && years === 0 && months < 3) timePassed.push(days + ' dia' + (days > 1 ? 's' : ''));
        
        return timeStr + ' - ' + (timePassed.length > 0 ? timePassed.join(' e ') + ' desde cirurgia' : 'Cirurgia recente');
    } catch (e) {
        console.error('Erro ao calcular data:', e, surgeryDate);
        return 'Data invalida';
    }
}

function renderSurgeries(surgeries) {
    var container = document.getElementById('surgeriesList');
    if (!container) return;
    
    if (!surgeries || surgeries.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><em>Nenhuma cirurgia registrada</em></div>';
        return;
    }
    
    var sorted = surgeries.slice().sort(function(a, b) { 
        return new Date(b.surgery_date) - new Date(a.surgery_date); 
    });
    
    var html = sorted.map(function(surgery) {
        var daysSince = calculateDaysSince(surgery.surgery_date);
        var evolutionBtnClass = 'btn-success';
        var evolutionBtnText = '<i class="bi bi-plus-circle"></i> Evolucao';
        
        if (daysSince >= 365) {
            evolutionBtnClass = 'btn-info';
            evolutionBtnText = '<i class="bi bi-star"></i> Resultado 1 Ano';
        } else if (daysSince >= 7) {
            evolutionBtnClass = 'btn-warning';
            evolutionBtnText = '<i class="bi bi-clipboard-pulse"></i> Evolucao 7 Dias';
        }
        
        var obsHtml = '';
        if (surgery.observations) {
            obsHtml = '<div class="mb-2"><strong>Observacoes:</strong><p class="mb-0 p-2 bg-light rounded" style="white-space: pre-wrap; font-size: 0.9rem;">' + surgery.observations + '</p></div>';
        }
        
        var typeHtml = '';
        if (surgery.surgery_type) {
            typeHtml = '<div class="mb-2"><span class="badge bg-info me-2">Tipo:</span><strong>' + surgery.surgery_type + '</strong></div>';
        }
        
        return '<div class="card mb-3 border-left border-success" style="border-left: 5px solid #198754;">' +
            '<div class="card-body">' +
                '<div class="row">' +
                    '<div class="col-md-8">' +
                        '<h6 class="mb-2 text-success"><i class="bi bi-calendar2-check"></i> <strong>' + calculateSurgeryTime(surgery.surgery_date) + '</strong></h6>' +
                        typeHtml +
                        '<div class="mb-2"><strong>Dados Cirurgicos:</strong><p class="mb-0 p-2 bg-light rounded" style="white-space: pre-wrap; font-size: 0.9rem;">' + surgery.surgical_data + '</p></div>' +
                        obsHtml +
                        '<small class="text-muted"><i class="bi bi-person-fill"></i> Dr. ' + surgery.doctor_name + '</small>' +
                        '<div id="evolutions-' + surgery.id + '" class="mt-2"></div>' +
                    '</div>' +
                    '<div class="col-md-4">' +
                        '<button class="btn btn-sm ' + evolutionBtnClass + ' w-100 mb-2" onclick="createEvolutionForSurgery(' + surgery.id + ', \'' + surgery.surgery_date + '\')">' + evolutionBtnText + '</button>' +
                        '<button class="btn btn-sm btn-outline-secondary w-100 mb-2" onclick="viewEvolutions(' + surgery.id + ')"><i class="bi bi-list-check"></i> Ver Evolucoes</button>' +
                        '<button class="btn btn-sm btn-outline-danger w-100" onclick="deleteSurgery(' + surgery.id + ')"><i class="bi bi-trash"></i> Deletar</button>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
    }).join('');
    
    container.innerHTML = html;
}

function viewEvolutions(surgeryId) {
    var pId = typeof patientId !== 'undefined' ? patientId : null;
    if (!pId) {
        var el = document.getElementById('detailPatientId');
        if (el) pId = el.value;
    }
    fetch('/api/patient/' + pId + '/surgery/' + surgeryId + '/evolutions')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var container = document.getElementById('evolutions-' + surgeryId);
            if (!container) return;
            if (!data.evolutions || data.evolutions.length === 0) {
                container.innerHTML = '<div class="alert alert-secondary py-1 px-2 mb-0"><small>Nenhuma evolucao registrada</small></div>';
                return;
            }
            
            var evoHtml = data.evolutions.map(function(e) {
                var badges = '';
                if (e.evolution_type === '7_days') {
                    if (e.has_necrosis) badges += '<span class="badge bg-danger me-1">Necrose</span>';
                    if (e.has_infection) badges += '<span class="badge bg-danger me-1">Infeccao</span>';
                    if (e.has_scabs) badges += '<span class="badge bg-warning text-dark me-1">Crostas</span>';
                    if (e.has_follicle_loss) badges += '<span class="badge bg-secondary me-1">Perda Foliculos</span>';
                } else if (e.evolution_type === '1_year') {
                    var resultColors = {otimo: 'success', bom: 'primary', medio: 'warning', ruim: 'danger'};
                    if (e.result_rating) badges += '<span class="badge bg-' + (resultColors[e.result_rating] || 'secondary') + ' me-1">' + e.result_rating.charAt(0).toUpperCase() + e.result_rating.slice(1) + '</span>';
                    if (e.needs_another_surgery) badges += '<span class="badge bg-info me-1">Nova Cirurgia</span>';
                }
                
                var date = new Date(e.evolution_date).toLocaleDateString('pt-BR');
                return '<div class="border-bottom pb-2 mb-2"><small class="text-muted">' + date + ' - Dr. ' + e.doctor_name + '</small><div>' + badges + '</div>' + (e.content ? '<p class="mb-0 small">' + e.content + '</p>' : '') + '</div>';
            }).join('');
            
            container.innerHTML = '<div class="border rounded p-2 bg-light"><strong class="d-block mb-2"><i class="bi bi-clipboard-data"></i> Evolucoes (' + data.evolutions.length + ')</strong>' + evoHtml + '</div>';
        })
        .catch(function(err) { console.error('Erro ao carregar evolucoes:', err); });
}

function calculateDaysSince(surgeryDate) {
    var dateStr = surgeryDate;
    if (surgeryDate.indexOf('/') !== -1) {
        var parts = surgeryDate.split('/');
        dateStr = parts[2] + '-' + parts[1] + '-' + parts[0];
    }
    var dateParts = dateStr.split('-').map(Number);
    var surgery = new Date(Date.UTC(dateParts[0], dateParts[1] - 1, dateParts[2]));
    var today = new Date();
    return Math.floor((today - surgery) / (1000 * 60 * 60 * 24));
}

function createEvolutionForSurgery(surgeryId, surgeryDate) {
    var daysSince = calculateDaysSince(surgeryDate);
    var modalHtml = '<div class="modal fade" id="surgeryEvolutionModal" tabindex="-1">' +
        '<div class="modal-dialog modal-lg">' +
            '<div class="modal-content">' +
                '<div class="modal-header bg-success text-white">' +
                    '<h5 class="modal-title"><i class="bi bi-clipboard-pulse"></i> Nova Evolucao Pos-Cirurgica</h5>' +
                    '<button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>' +
                '</div>' +
                '<div class="modal-body">' +
                    '<div class="alert alert-secondary mb-3"><i class="bi bi-clock"></i> <strong>' + daysSince + ' dias</strong> desde a cirurgia</div>' +
                    '<div class="mb-4">' +
                        '<label class="form-label fw-bold">Tipo de Evolucao:</label>' +
                        '<div class="btn-group w-100" role="group">' +
                            '<input type="radio" class="btn-check" name="evolution_type" id="evo_rotina" value="general" checked>' +
                            '<label class="btn btn-outline-secondary" for="evo_rotina">Rotina</label>' +
                            '<input type="radio" class="btn-check" name="evolution_type" id="evo_7dias" value="7_days">' +
                            '<label class="btn btn-outline-warning" for="evo_7dias">7 Dias</label>' +
                            '<input type="radio" class="btn-check" name="evolution_type" id="evo_1ano" value="1_year">' +
                            '<label class="btn btn-outline-info" for="evo_1ano">1 Ano</label>' +
                        '</div>' +
                    '</div>' +
                    '<div id="evolutionFormContainer"></div>' +
                '</div>' +
                '<div class="modal-footer">' +
                    '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>' +
                    '<button type="button" class="btn btn-success" id="btnSaveEvolution">Salvar Evolucao</button>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '</div>';
    
    var existingModal = document.getElementById('surgeryEvolutionModal');
    if (existingModal) existingModal.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    document.getElementById('evolutionFormContainer').innerHTML = getEvolutionFormHtml('general');
    
    document.getElementById('btnSaveEvolution').addEventListener('click', function() {
        saveSurgeryEvolution(surgeryId);
    });
    
    document.querySelectorAll('input[name="evolution_type"]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            document.getElementById('evolutionFormContainer').innerHTML = getEvolutionFormHtml(this.value);
        });
    });
    
    var modal = new bootstrap.Modal(document.getElementById('surgeryEvolutionModal'));
    modal.show();
}
window.createEvolutionForSurgery = createEvolutionForSurgery;

function getEvolutionFormHtml(type) {
    if (type === '1_year') {
        return '<div class="mb-3">' +
            '<label class="form-label fw-bold">Resultado:</label>' +
            '<div class="btn-group w-100" role="group">' +
                '<input type="radio" class="btn-check" name="result_rating" id="result_otimo" value="otimo">' +
                '<label class="btn btn-outline-success" for="result_otimo">Otimo</label>' +
                '<input type="radio" class="btn-check" name="result_rating" id="result_bom" value="bom">' +
                '<label class="btn btn-outline-primary" for="result_bom">Bom</label>' +
                '<input type="radio" class="btn-check" name="result_rating" id="result_medio" value="medio">' +
                '<label class="btn btn-outline-warning" for="result_medio">Medio</label>' +
                '<input type="radio" class="btn-check" name="result_rating" id="result_ruim" value="ruim">' +
                '<label class="btn btn-outline-danger" for="result_ruim">Ruim</label>' +
            '</div>' +
        '</div>' +
        '<div class="mb-3">' +
            '<div class="form-check form-switch">' +
                '<input class="form-check-input" type="checkbox" id="needs_another_surgery">' +
                '<label class="form-check-label" for="needs_another_surgery">Indicacao de nova cirurgia</label>' +
            '</div>' +
        '</div>' +
        '<textarea class="form-control" id="evolution_content" rows="4" placeholder="Observacoes..."></textarea>';
    } else if (type === '7_days') {
        return '<div class="row mb-3">' +
            '<div class="col-6"><div class="form-check"><input class="form-check-input" type="checkbox" id="has_necrosis"><label class="form-check-label">Necrose</label></div></div>' +
            '<div class="col-6"><div class="form-check"><input class="form-check-input" type="checkbox" id="has_scabs"><label class="form-check-label">Crostas</label></div></div>' +
            '<div class="col-6"><div class="form-check"><input class="form-check-input" type="checkbox" id="has_infection"><label class="form-check-label">Infeccao</label></div></div>' +
            '<div class="col-6"><div class="form-check"><input class="form-check-input" type="checkbox" id="has_follicle_loss"><label class="form-check-label">Perda Foliculos</label></div></div>' +
        '</div>' +
        '<textarea class="form-control" id="evolution_content" rows="4" placeholder="Observacoes..."></textarea>';
    }
    return '<textarea class="form-control" id="evolution_content" rows="6" placeholder="Descricao da evolucao..."></textarea>';
}

function saveSurgeryEvolution(surgeryId) {
    var pId = typeof patientId !== 'undefined' ? patientId : null;
    if (!pId) {
        var el = document.getElementById('detailPatientId');
        if (el) pId = el.value;
    }
    
    var contentEl = document.getElementById('evolution_content');
    var typeEl = document.querySelector('input[name="evolution_type"]:checked');
    var necrosisEl = document.getElementById('has_necrosis');
    var scabsEl = document.getElementById('has_scabs');
    var infectionEl = document.getElementById('has_infection');
    var follicleEl = document.getElementById('has_follicle_loss');
    var ratingEl = document.querySelector('input[name="result_rating"]:checked');
    var needsSurgeryEl = document.getElementById('needs_another_surgery');
    
    var data = {
        content: contentEl ? contentEl.value : '',
        evolution_type: typeEl ? typeEl.value : 'general',
        has_necrosis: necrosisEl ? necrosisEl.checked : false,
        has_scabs: scabsEl ? scabsEl.checked : false,
        has_infection: infectionEl ? infectionEl.checked : false,
        has_follicle_loss: follicleEl ? follicleEl.checked : false,
        result_rating: ratingEl ? ratingEl.value : null,
        needs_another_surgery: needsSurgeryEl ? needsSurgeryEl.checked : false
    };
    
    fetch('/api/patient/' + pId + '/surgery/' + surgeryId + '/evolution', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': typeof getCSRFToken === 'function' ? getCSRFToken() : ''
        },
        body: JSON.stringify(data)
    })
    .then(function(r) { return r.json(); })
    .then(function(result) {
        if (result.success) {
            bootstrap.Modal.getInstance(document.getElementById('surgeryEvolutionModal')).hide();
            if (typeof showAlert === 'function') showAlert('Evolucao salva!', 'success');
            window.loadSurgeries();
        } else {
            if (typeof showAlert === 'function') showAlert('Erro: ' + result.error, 'danger');
        }
    })
    .catch(function(err) { console.error('Erro:', err); });
}

window.viewEvolutions = viewEvolutions;

document.addEventListener('DOMContentLoaded', function() {
    var surgeriesList = document.getElementById('surgeriesList');
    if (surgeriesList && typeof patientId !== 'undefined') {
        window.loadSurgeries();
    }
});
