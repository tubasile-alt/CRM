console.log('prontuario.js v=20260306-STABLE');
let timerInterval = null;
let timerStartTime = null;
let currentCategory = 'patologia';
let cosmeticProcedures = [];

function handleCategoryChange(event) {
    const val = (event && event.target) ? event.target.value : (typeof event === 'string' ? event : 'patologia');
    console.log('[PRONTUARIO] Categoria:', val);

    const s = {
        geral: document.getElementById('section_geral'),
        cosm: document.getElementById('section_cosmiatria'),
        trans: document.getElementById('section_transplante'),
        indic: document.getElementById('indicatedProceduresSection'),
        cond: document.getElementById('cosmeticConductSection'),
        panelPat: document.getElementById('panel_patologia'),
        panelCosm: document.getElementById('panel_cosmiatria')
    };

    const show = (el) => { if (el) { el.classList.remove('d-none'); el.style.setProperty('display', 'block', 'important'); } };
    const hide = (el) => { if (el) { el.classList.add('d-none'); el.style.setProperty('display', 'none', 'important'); } };

    show(s.geral);
    if (val === 'cosmiatria') {
        show(s.cosm); show(s.cond); show(s.panelCosm);
        hide(s.trans); hide(s.indic); hide(s.panelPat);
    } else if (val === 'transplante_capilar') {
        show(s.trans);
        hide(s.cosm); hide(s.cond); hide(s.indic); hide(s.panelCosm); hide(s.panelPat);
    } else {
        show(s.indic); show(s.cond); show(s.panelPat);
        hide(s.cosm); hide(s.trans); hide(s.panelCosm);
    }

    currentCategory = val;
    if ((val === 'cosmiatria' || val === 'transplante_capilar') && !timerStartTime) startTimer();
}

function startTimer() {
    if (timerInterval) return;
    timerStartTime = Date.now();
    const btn = document.getElementById('startTimer');
    const disp = document.getElementById('timerDisplay');
    if (btn) {
        btn.innerHTML = '<i class="bi bi-stop-circle"></i> Parar Atendimento';
        btn.classList.replace('btn-success', 'btn-danger');
    }
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - timerStartTime) / 1000);
        const m = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const s = String(elapsed % 60).padStart(2, '0');
        if (disp) disp.textContent = `${m}:${s}`;
    }, 1000);
}

function renderCosmeticProcedures() {
    const tbody = document.getElementById('cosmeticPlanBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (cosmeticProcedures.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3 small">Nenhum procedimento planejado</td></tr>';
        return;
    }
    cosmeticProcedures.forEach((p, i) => {
        const row = tbody.insertRow();
        row.innerHTML = `<td class="ps-3">${p.name}</td><td>R$ ${p.value.toFixed(2)}</td><td>${p.months} meses</td><td class="text-center"><button class="btn btn-sm text-danger" onclick="removeCosmeticProcedure(${i})"><i class="bi bi-trash"></i></button></td>`;
    });
    const total = cosmeticProcedures.reduce((sum, p) => sum + p.value, 0);
    const el = document.getElementById('cosmeticTotal');
    if (el) el.textContent = total.toLocaleString('pt-BR', {minimumFractionDigits: 2});
}

function addCosmeticProcedure() {
    const n = document.getElementById('newProcedureName').value;
    const v = parseFloat(document.getElementById('newProcedureValue').value) || 0;
    const m = parseInt(document.getElementById('newProcedureMonths').value) || 6;
    if (n && v > 0) {
        cosmeticProcedures.push({name: n, value: v, months: m});
        document.getElementById('newProcedureName').value = '';
        document.getElementById('newProcedureValue').value = '';
        renderCosmeticProcedures();
        renderCosmeticConduct();
    }
}

function removeCosmeticProcedure(i) {
    cosmeticProcedures.splice(i, 1);
    renderCosmeticProcedures();
    renderCosmeticConduct();
}

function renderCosmeticConduct() {
    const tbody = document.getElementById('cosmeticConductBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (cosmeticProcedures.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-3">Nenhum item pendente</td></tr>';
        return;
    }
    cosmeticProcedures.forEach(p => {
        const row = tbody.insertRow();
        row.innerHTML = `<td class="ps-3 small">${p.name}</td><td class="small">R$ ${p.value.toFixed(2)}</td><td class="text-center"><span class="badge bg-danger">PENDENTE</span></td>`;
    });
}

function startDictation(id, event) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return alert('Navegador não suporta voz');
    const rec = new SpeechRecognition();
    rec.lang = 'pt-BR';
    rec.onresult = (e) => {
        const t = document.getElementById(id);
        if (t) t.value += (t.value ? ' ' : '') + e.results[0][0].transcript;
    };
    rec.start();
    const b = event.target.closest('button');
    if (b) {
        const old = b.innerHTML; b.innerHTML = '<i class="bi bi-mic-fill text-danger"></i>...';
        rec.onend = () => b.innerHTML = old;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[name="category"]').forEach(i => i.addEventListener('change', handleCategoryChange));
    setTimeout(() => {
        const a = document.querySelector('input[name="category"]:checked');
        handleCategoryChange(a ? a.value : 'patologia');
    }, 500);
});
