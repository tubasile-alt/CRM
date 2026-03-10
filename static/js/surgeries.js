// ========== GERENCIAR CIRURGIAS ==========

window.saveSurgery = function () {
  console.log("saveSurgery chamada");

  const pId = window.patientId || document.getElementById("detailPatientId")?.value;

  if (!pId) {
    showAlert?.("Erro: ID do paciente não encontrado.", "danger");
    return;
  }

  const surgeryDate =
    document.getElementById("surgeryDate")?.value ||
    document.getElementById("surgeryModalDate")?.value ||
    "";

  const surgicalData =
    document.getElementById("surgicalData")?.value?.trim() ||
    document.getElementById("surgeryModalSurgicalPlanning")?.value?.trim() ||
    "";

  const observations =
    document.getElementById("surgeryObservations")?.value?.trim() ||
    document.getElementById("surgeryModalComplications")?.value?.trim() ||
    "";

  const surgeryTypes = [];
  [
    "surgeryTypeCapilar",
    "surgeryTypeBodyHair",
    "surgeryTypeSobrancelhas",
    "surgeryTypeBarba",
    "surgeryTypeRetoque"
  ].forEach((id) => {
    const cb = document.getElementById(id);
    if (cb?.checked) surgeryTypes.push(cb.value);
  });

  const surgeryType = surgeryTypes.join(", ");

  if (!surgeryDate) {
    showAlert?.("Selecione a data da cirurgia!", "warning");
    return;
  }

  if (!surgicalData) {
    showAlert?.("Preencha os dados cirúrgicos!", "warning");
    return;
  }

  fetch(`/api/patient/${pId}/surgery`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": typeof getCSRFToken === "function" ? getCSRFToken() : ""
    },
    body: JSON.stringify({
      surgery_date: surgeryDate.split("T")[0],
      surgical_data: surgicalData,
      observations: observations,
      surgery_type: surgeryType
    })
  })
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then((result) => {
      if (result.success) {
        showAlert?.("Cirurgia registrada com sucesso!", "success");

        [
          "surgeryDate",
          "surgicalData",
          "surgeryObservations",
          "surgeryModalDate",
          "surgeryModalSurgicalPlanning",
          "surgeryModalComplications"
        ].forEach((id) => {
          const el = document.getElementById(id);
          if (el) el.value = "";
        });

        [
          "surgeryTypeCapilar",
          "surgeryTypeBodyHair",
          "surgeryTypeSobrancelhas",
          "surgeryTypeBarba",
          "surgeryTypeRetoque"
        ].forEach((id) => {
          const cb = document.getElementById(id);
          if (cb) cb.checked = false;
        });

        if (typeof window.loadSurgeries === "function") {
          window.loadSurgeries();
        }
      } else {
        showAlert?.(`Erro: ${result.error || "Erro ao salvar"}`, "danger");
      }
    })
    .catch((err) => {
      console.error("Erro ao salvar cirurgia:", err);
      showAlert?.("Erro ao salvar cirurgia", "danger");
    });
};

window.loadSurgeries = function () {
    console.log("loadSurgeries chamada");

    var pId = typeof patientId !== "undefined" ? patientId : null;
    if (!pId) {
        var el = document.getElementById("detailPatientId");
        if (el) pId = el.value;
    }

    if (!pId) {
        console.warn("loadSurgeries: pId nao encontrado");
        return;
    }

    fetch("/api/patient/" + pId + "/surgeries")
        .then(function (r) {
            if (!r.ok) throw new Error("Servidor retornou erro");
            return r.json();
        })
        .then(function (surgeries) {
            console.log("Cirurgias carregadas:", surgeries);
            renderSurgeries(surgeries);
        })
        .catch(function (err) {
            console.error("Erro ao carregar cirurgias:", err);
        });
};

window.deleteSurgery = function (surgeryId) {
    if (!confirm("Tem certeza que deseja deletar esta cirurgia?")) return;

    fetch("/api/surgery/" + parseInt(surgeryId, 10), {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": typeof getCSRFToken === "function" ? getCSRFToken() : ""
        }
    })
        .then(function (r) {
            if (!r.ok) throw new Error("Falha na resposta do servidor");
            return r.json();
        })
        .then(function (result) {
            if (result.success) {
                if (typeof showAlert === "function") showAlert("Cirurgia deletada!", "success");
                if (typeof window.loadSurgeries === "function") window.loadSurgeries();
            } else {
                if (typeof showAlert === "function") showAlert("Erro: " + (result.error || "Erro ao deletar"), "danger");
            }
        })
        .catch(function (err) {
            console.error("Erro ao deletar cirurgia:", err);
            if (typeof showAlert === "function") showAlert("Erro ao deletar cirurgia", "danger");
        });
};

function calculateDaysSince(surgeryDate) {
    var dateStr = surgeryDate;

    if (surgeryDate.indexOf("/") !== -1) {
        var parts = surgeryDate.split("/");
        dateStr = parts[2] + "-" + parts[1] + "-" + parts[0];
    }

    var dateParts = dateStr.split("-").map(Number);
    var surgery = new Date(Date.UTC(dateParts[0], dateParts[1] - 1, dateParts[2]));
    var today = new Date();

    return Math.floor((today - surgery) / (1000 * 60 * 60 * 24));
}

function calculateSurgeryTime(surgeryDate) {
    try {
        var dateStr = surgeryDate;

        if (surgeryDate.indexOf("/") !== -1) {
            var parts = surgeryDate.split("/");
            dateStr = parts[2] + "-" + parts[1] + "-" + parts[0];
        }

        var dateParts = dateStr.split("-").map(Number);
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

        var dayStr = day.toString().padStart(2, "0");
        var monthStr = month.toString().padStart(2, "0");
        var timeStr = dayStr + "/" + monthStr + "/" + year;

        var timePassed = [];
        if (years > 0) timePassed.push(years + " ano" + (years > 1 ? "s" : ""));
        if (months > 0) timePassed.push(months + " mes" + (months > 1 ? "es" : ""));
        if (days > 0 && years === 0 && months < 3) timePassed.push(days + " dia" + (days > 1 ? "s" : ""));

        return timeStr + " - " + (timePassed.length > 0 ? timePassed.join(" e ") + " desde cirurgia" : "Cirurgia recente");
    } catch (e) {
        console.error("Erro ao calcular data:", e, surgeryDate);
        return "Data invalida";
    }
}

function getSuggestedEvolutionType(daysSince) {
    if (daysSince >= 300) return "1_year";
    if (daysSince >= 120) return "5_months";
    if (daysSince >= 5) return "7_days";
    return "general";
}

function renderSurgeries(surgeries) {
    var container = document.getElementById("surgeriesList");
    if (!container) return;

    if (!surgeries || surgeries.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><em>Nenhuma cirurgia registrada</em></div>';
        return;
    }

    var sorted = surgeries.slice().sort(function (a, b) {
        return new Date(b.surgery_date_iso || b.surgery_date) - new Date(a.surgery_date_iso || a.surgery_date);
    });

    var html = sorted.map(function (surgery) {
        var daysSince = calculateDaysSince(surgery.surgery_date_iso || surgery.surgery_date);
        var suggestedType = getSuggestedEvolutionType(daysSince);

        var evolutionBtnClass = "btn-success";
        var evolutionBtnText = '<i class="bi bi-plus-circle"></i> Evolucao';

        if (suggestedType === "1_year") {
            evolutionBtnClass = "btn-info";
            evolutionBtnText = '<i class="bi bi-star"></i> Evolucao 1 Ano';
        } else if (suggestedType === "5_months") {
            evolutionBtnClass = "btn-primary";
            evolutionBtnText = '<i class="bi bi-clipboard2-pulse"></i> Evolucao 5 Meses';
        } else if (suggestedType === "7_days") {
            evolutionBtnClass = "btn-warning";
            evolutionBtnText = '<i class="bi bi-clipboard-pulse"></i> Evolucao 7 Dias';
        }

        var obsHtml = "";
        if (surgery.observations) {
            obsHtml =
                '<div class="mb-2"><strong>Observacoes:</strong><p class="mb-0 p-2 bg-light rounded" style="white-space: pre-wrap; font-size: 0.9rem;">' +
                surgery.observations +
                "</p></div>";
        }

        var typeHtml = "";
        if (surgery.surgery_type) {
            typeHtml =
                '<div class="mb-2"><span class="badge bg-info me-2">Tipo:</span><strong>' +
                surgery.surgery_type +
                "</strong></div>";
        }

        return (
            '<div class="card mb-3 border-left border-success" style="border-left: 5px solid #198754;">' +
            '<div class="card-body">' +
            '<div class="row">' +
            '<div class="col-md-8">' +
            '<h6 class="mb-2 text-success"><i class="bi bi-calendar2-check"></i> <strong>' +
            calculateSurgeryTime(surgery.surgery_date) +
            "</strong></h6>" +
            typeHtml +
            '<div class="mb-2"><strong>Dados Cirurgicos:</strong><p class="mb-0 p-2 bg-light rounded" style="white-space: pre-wrap; font-size: 0.9rem;">' +
            (surgery.surgical_data || "") +
            "</p></div>" +
            obsHtml +
            '<small class="text-muted"><i class="bi bi-person-fill"></i> Dr. ' +
            surgery.doctor_name +
            "</small>" +
            '<div id="evolutions-' +
            surgery.id +
            '" class="mt-2"></div>' +
            "</div>" +
            '<div class="col-md-4">' +
            '<button class="btn btn-sm ' +
            evolutionBtnClass +
            ' w-100 mb-2" onclick="createEvolutionForSurgery(' +
            surgery.id +
            ", '" +
            surgery.surgery_date +
            "')\">" +
            evolutionBtnText +
            "</button>" +
            '<button class="btn btn-sm btn-outline-secondary w-100 mb-2" onclick="viewEvolutions(' +
            surgery.id +
            ')"><i class="bi bi-list-check"></i> Ver Evolucoes</button>' +
            '<button class="btn btn-sm btn-outline-danger w-100" onclick="deleteSurgery(' +
            surgery.id +
            ')"><i class="bi bi-trash"></i> Deletar</button>' +
            "</div>" +
            "</div>" +
            "</div>" +
            "</div>"
        );
    }).join("");

    container.innerHTML = html;
}

function getBooleanBadge(value, yesText, noText, yesClass, noClass) {
    if (value === true) return '<span class="badge bg-' + (yesClass || "success") + ' me-1">' + yesText + "</span>";
    if (value === false) return '<span class="badge bg-' + (noClass || "secondary") + ' me-1">' + noText + "</span>";
    return "";
}

function viewEvolutions(surgeryId) {
    fetch("/api/surgery/" + surgeryId + "/evolutions")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var container = document.getElementById("evolutions-" + surgeryId);
            if (!container) return;

            if (!data.evolutions || data.evolutions.length === 0) {
                container.innerHTML = '<div class="alert alert-secondary py-1 px-2 mb-0"><small>Nenhuma evolucao registrada</small></div>';
                return;
            }

            var evoHtml = data.evolutions.map(function (e) {
                var badges = "";

                if (e.evolution_type === "7_days") {
                    if (e.has_necrosis) badges += '<span class="badge bg-danger me-1">Necrose</span>';
                    if (e.has_scabs) badges += '<span class="badge bg-warning text-dark me-1">Crostas</span>';
                    if (e.has_infection) badges += '<span class="badge bg-danger me-1">Infeccao</span>';
                    if (e.has_follicle_loss) badges += '<span class="badge bg-secondary me-1">Perda foliculos</span>';
                    if (e.has_folliculitis_acute) badges += '<span class="badge bg-warning text-dark me-1">Foliculite aguda</span>';
                    if (e.has_folliculitis_chronic) badges += '<span class="badge bg-dark me-1">Foliculite cronica</span>';
                    if (e.has_rarefaction) badges += '<span class="badge bg-secondary me-1">Rarefacao</span>';
                    if (e.has_local_failure) badges += '<span class="badge bg-danger me-1">Falha localizada</span>';
                }

                if (e.evolution_type === "5_months") {
                    if (e.has_necrosis) badges += '<span class="badge bg-danger me-1">Necrose</span>';
                    if (e.has_scabs) badges += '<span class="badge bg-warning text-dark me-1">Crostas</span>';
                    if (e.has_infection) badges += '<span class="badge bg-danger me-1">Infeccao</span>';
                    if (e.has_follicle_loss) badges += '<span class="badge bg-secondary me-1">Perda foliculos</span>';
                    if (e.has_folliculitis_acute) badges += '<span class="badge bg-warning text-dark me-1">Foliculite aguda</span>';
                    if (e.has_folliculitis_chronic) badges += '<span class="badge bg-dark me-1">Foliculite cronica</span>';
                    if (e.has_rarefaction) badges += '<span class="badge bg-secondary me-1">Rarefacao</span>';
                    if (e.has_local_failure) badges += '<span class="badge bg-danger me-1">Falha localizada</span>';

                    badges += getBooleanBadge(e.patient_satisfied, "Paciente satisfeito", "Paciente insatisfeito", "success", "danger");
                    badges += getBooleanBadge(e.result_within_expected, "Dentro do esperado", "Fora do esperado", "primary", "warning");
                    badges += getBooleanBadge(e.using_oral_medication, "Usando medicacao oral", "Sem medicacao oral", "info", "secondary");
                }

                if (e.evolution_type === "1_year") {
                    if (e.has_rarefaction) badges += '<span class="badge bg-secondary me-1">Rarefacao</span>';
                    if (e.has_local_failure) badges += '<span class="badge bg-danger me-1">Falha localizada</span>';

                    badges += getBooleanBadge(e.patient_satisfied, "Paciente satisfeito", "Paciente insatisfeito", "success", "danger");
                    badges += getBooleanBadge(e.needs_another_surgery, "Nova cirurgia", "Sem nova cirurgia", "info", "secondary");
                    badges += getBooleanBadge(e.needs_body_hair, "Indicar body hair", "Sem body hair", "dark", "secondary");
                    badges += getBooleanBadge(e.needs_touch_up, "Precisa retoque", "Sem retoque", "warning", "secondary");
                }

                if (e.evolution_type === "general") {
                    badges += '<span class="badge bg-secondary me-1">Retorno livre</span>';
                }

                var labelMap = {
                    general: "Retorno livre",
                    "7_days": "Retorno 7 dias",
                    "5_months": "Retorno 5 meses",
                    "1_year": "Retorno 1 ano"
                };

                var date = new Date(e.evolution_date).toLocaleDateString("pt-BR");

                return (
                    '<div class="border-bottom pb-2 mb-2">' +
                    '<small class="text-muted">' + date + " - Dr. " + e.doctor_name + "</small>" +
                    '<div class="mb-1"><span class="badge bg-primary me-1">' + (labelMap[e.evolution_type] || e.evolution_type) + "</span></div>" +
                    '<div>' + badges + "</div>" +
                    (e.content ? '<p class="mb-0 small mt-2" style="white-space: pre-wrap;">' + e.content + "</p>" : "") +
                    "</div>"
                );
            }).join("");

            container.innerHTML =
                '<div class="border rounded p-2 bg-light"><strong class="d-block mb-2"><i class="bi bi-clipboard-data"></i> Evolucoes (' +
                data.evolutions.length +
                ")</strong>" +
                evoHtml +
                "</div>";
        })
        .catch(function (err) {
            console.error("Erro ao carregar evolucoes:", err);
        });
}

function createEvolutionForSurgery(surgeryId, surgeryDate) {
    var daysSince = calculateDaysSince(surgeryDate);
    var suggestedType = getSuggestedEvolutionType(daysSince);

    var modalHtml =
        '<div class="modal fade" id="surgeryEvolutionModal" tabindex="-1">' +
        '<div class="modal-dialog modal-lg">' +
        '<div class="modal-content">' +
        '<div class="modal-header bg-success text-white">' +
        '<h5 class="modal-title"><i class="bi bi-clipboard-pulse"></i> Nova Evolucao Pos-Cirurgica</h5>' +
        '<button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>' +
        "</div>" +
        '<div class="modal-body">' +
        '<div class="alert alert-secondary mb-3"><i class="bi bi-clock"></i> <strong>' + daysSince + " dias</strong> desde a cirurgia</div>" +
        '<div class="mb-4">' +
        '<label class="form-label fw-bold">Tipo de Retorno:</label>' +
        '<select class="form-select" id="evolution_type_select">' +
        '<option value="general">Retorno livre</option>' +
        '<option value="7_days">Retorno 7 dias</option>' +
        '<option value="5_months">Retorno 5 meses</option>' +
        '<option value="1_year">Retorno 1 ano</option>' +
        "</select>" +
        "</div>" +
        '<div id="evolutionFormContainer"></div>' +
        "</div>" +
        '<div class="modal-footer">' +
        '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>' +
        '<button type="button" class="btn btn-success" id="btnSaveEvolution">Salvar Evolucao</button>' +
        "</div>" +
        "</div>" +
        "</div>" +
        "</div>";

    var existingModal = document.getElementById("surgeryEvolutionModal");
    if (existingModal) existingModal.remove();

    document.body.insertAdjacentHTML("beforeend", modalHtml);

    var select = document.getElementById("evolution_type_select");
    select.value = suggestedType;
    document.getElementById("evolutionFormContainer").innerHTML = getEvolutionFormHtml(suggestedType);

    document.getElementById("btnSaveEvolution").addEventListener("click", function () {
        saveSurgeryEvolution(surgeryId);
    });

    select.addEventListener("change", function () {
        document.getElementById("evolutionFormContainer").innerHTML = getEvolutionFormHtml(this.value);
    });

    var modal = new bootstrap.Modal(document.getElementById("surgeryEvolutionModal"));
    modal.show();
}
window.createEvolutionForSurgery = createEvolutionForSurgery;

function getCheck(id, label) {
    return (
        '<div class="col-md-6 mb-2">' +
        '<div class="form-check">' +
        '<input class="form-check-input" type="checkbox" id="' + id + '">' +
        '<label class="form-check-label" for="' + id + '">' + label + "</label>" +
        "</div>" +
        "</div>"
    );
}

function getBooleanRadios(name, label) {
    return (
        '<div class="mb-3">' +
        '<label class="form-label fw-bold d-block">' + label + "</label>" +
        '<div class="btn-group w-100" role="group">' +
        '<input type="radio" class="btn-check" name="' + name + '" id="' + name + '_sim" value="true">' +
        '<label class="btn btn-outline-success" for="' + name + '_sim">Sim</label>' +
        '<input type="radio" class="btn-check" name="' + name + '" id="' + name + '_nao" value="false">' +
        '<label class="btn btn-outline-danger" for="' + name + '_nao">Nao</label>' +
        "</div>" +
        "</div>"
    );
}

function getBaseSurgicalChecklist() {
    return (
        '<div class="row">' +
        getCheck("has_necrosis", "Necrose") +
        getCheck("has_scabs", "Crostas") +
        getCheck("has_infection", "Infeccao secundaria") +
        getCheck("has_follicle_loss", "Perda de foliculos") +
        getCheck("has_folliculitis_acute", "Foliculite aguda") +
        getCheck("has_folliculitis_chronic", "Foliculite cronica") +
        getCheck("has_rarefaction", "Rarefacao capilar") +
        getCheck("has_local_failure", "Falha localizada") +
        "</div>"
    );
}

function getEvolutionFormHtml(type) {
    if (type === "7_days") {
        return (
            '<div class="mb-3"><label class="form-label fw-bold">Checklist 7 dias</label>' +
            getBaseSurgicalChecklist() +
            "</div>" +
            '<div class="mb-3">' +
            '<label class="form-label fw-bold">Observacoes</label>' +
            '<textarea class="form-control" id="evolution_content" rows="4" placeholder="Descreva a evolucao..."></textarea>' +
            "</div>"
        );
    }

    if (type === "5_months") {
        return (
            '<div class="mb-3"><label class="form-label fw-bold">Checklist clinico</label>' +
            getBaseSurgicalChecklist() +
            "</div>" +
            getBooleanRadios("patient_satisfied", "Paciente esta satisfeito?") +
            getBooleanRadios("result_within_expected", "Resultado esta dentro do esperado?") +
            getBooleanRadios("using_oral_medication", "Paciente faz uso de medicacoes orais?") +
            '<div class="mb-3">' +
            '<label class="form-label fw-bold">Observacoes</label>' +
            '<textarea class="form-control" id="evolution_content" rows="4" placeholder="Descreva a evolucao de 5 meses..."></textarea>' +
            "</div>"
        );
    }

    if (type === "1_year") {
        return (
            '<div class="mb-3"><label class="form-label fw-bold">Achados de 1 ano</label>' +
            '<div class="row">' +
            getCheck("has_rarefaction", "Ficou ralo") +
            getCheck("has_local_failure", "Ficou com falha") +
            getCheck("needs_another_surgery", "Tem indicacao de nova cirurgia") +
            getCheck("needs_body_hair", "Tem indicacao de body hair") +
            getCheck("needs_touch_up", "Precisa retoque") +
            "</div>' +
            "</div>" +
            getBooleanRadios("patient_satisfied", "Paciente esta satisfeito?") +
            '<div class="mb-3">' +
            '<label class="form-label fw-bold">Observacoes</label>' +
            '<textarea class="form-control" id="evolution_content" rows="4" placeholder="Descreva o resultado de 1 ano..."></textarea>' +
            "</div>"
        );
    }

    return (
        '<div class="mb-3">' +
        '<label class="form-label fw-bold">Observacoes</label>' +
        '<textarea class="form-control" id="evolution_content" rows="6" placeholder="Descricao da evolucao..."></textarea>' +
        "</div>"
    );
}

function getRadioBooleanValue(name) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    if (!el) return null;
    return el.value === "true";
}

function saveSurgeryEvolution(surgeryId) {
    var contentEl = document.getElementById("evolution_content");
    var typeEl = document.getElementById("evolution_type_select");

    var data = {
        content: contentEl ? contentEl.value : "",
        evolution_type: typeEl ? typeEl.value : "general",

        has_necrosis: !!document.getElementById("has_necrosis")?.checked,
        has_scabs: !!document.getElementById("has_scabs")?.checked,
        has_infection: !!document.getElementById("has_infection")?.checked,
        has_follicle_loss: !!document.getElementById("has_follicle_loss")?.checked,

        has_folliculitis_acute: !!document.getElementById("has_folliculitis_acute")?.checked,
        has_folliculitis_chronic: !!document.getElementById("has_folliculitis_chronic")?.checked,
        has_rarefaction: !!document.getElementById("has_rarefaction")?.checked,
        has_local_failure: !!document.getElementById("has_local_failure")?.checked,

        patient_satisfied: getRadioBooleanValue("patient_satisfied"),
        result_within_expected: getRadioBooleanValue("result_within_expected"),
        using_oral_medication: getRadioBooleanValue("using_oral_medication"),

        needs_another_surgery: !!document.getElementById("needs_another_surgery")?.checked,
        needs_body_hair: !!document.getElementById("needs_body_hair")?.checked,
        needs_touch_up: !!document.getElementById("needs_touch_up")?.checked
    };

    fetch("/api/surgery/" + surgeryId + "/evolution", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": typeof getCSRFToken === "function" ? getCSRFToken() : ""
        },
        body: JSON.stringify(data)
    })
        .then(function (r) { return r.json(); })
        .then(function (result) {
            if (result.success) {
                var modalInstance = bootstrap.Modal.getInstance(document.getElementById("surgeryEvolutionModal"));
                if (modalInstance) modalInstance.hide();
                if (typeof showAlert === "function") showAlert("Evolucao salva!", "success");
                window.loadSurgeries();
            } else {
                if (typeof showAlert === "function") showAlert("Erro: " + (result.error || "Erro ao salvar"), "danger");
            }
        })
        .catch(function (err) {
            console.error("Erro:", err);
            if (typeof showAlert === "function") showAlert("Erro ao salvar evolucao", "danger");
        });
}

window.viewEvolutions = viewEvolutions;

document.addEventListener("DOMContentLoaded", function () {
    var surgeriesList = document.getElementById("surgeriesList");
    if (surgeriesList && typeof patientId !== "undefined") {
        window.loadSurgeries();
    }
});