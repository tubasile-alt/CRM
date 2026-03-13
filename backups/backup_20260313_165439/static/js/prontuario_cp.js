(function () {
    'use strict';

    const root = document.getElementById('cp-root');
    if (!root) return;

    const DP_ID = parseInt(root.dataset.dpId, 10);
    const READ_ONLY = root.dataset.readOnly === 'true';
    const ROLE_CLINICO = root.dataset.roleClinco || root.getAttribute('data-role-clinico') || 'DERM';

    let encounterId = root.dataset.encounterId ? parseInt(root.dataset.encounterId, 10) : null;
    let autosaveTimer = null;
    let autosaveLastAt = null;

    // ===== PROCEDURES BY CATEGORY =====
    const PROCEDURES = {
        FACE: ['Rinoplastia', 'Ritidoplastia (Face)', 'Blefaroplastia', 'Otoplastia',
               'Mentoplastia', 'Bichectomia', 'Lipoenxertia Facial', 'Frontoplastia'],
        MAMA: ['Mamoplastia Redutora', 'Mamoplastia de Aumento', 'Mastopexia',
               'Mastopexia com Prótese', 'Cirurgia Pós-Bariátrica Mama', 'Mamoplastia Masculina'],
        CORPORAL: ['Abdominoplastia', 'Lipoaspiração', 'Lipoescultura', 'Miniabdominoplastia',
                   'Cirurgia Pós-Bariátrica Corporal', 'Ninfoplastia', 'Dermolipectomia Crural']
    };

    const IMPLANT_PROCS = ['Mamoplastia de Aumento', 'Mastopexia com Prótese'];
    const LIPO_PROCS = ['Lipoaspiração', 'Lipoescultura'];

    // ===== TIMER =====
    let timerSeconds = 0;
    let timerRunning = true;
    let timerInterval = null;

    function startTimer() {
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            if (timerRunning) {
                timerSeconds++;
                updateTimerDisplay();
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        const h = Math.floor(timerSeconds / 3600);
        const m = Math.floor((timerSeconds % 3600) / 60);
        const s = timerSeconds % 60;
        const el = document.getElementById('cpTimerDisplay');
        if (el) el.textContent = `${pad(h)}:${pad(m)}:${pad(s)}`;
    }

    function pad(n) { return String(n).padStart(2, '0'); }

    const timerToggle = document.getElementById('cpTimerToggle');
    const timerIcon = document.getElementById('cpTimerIcon');
    if (timerToggle) {
        timerToggle.addEventListener('click', () => {
            timerRunning = !timerRunning;
            timerIcon.className = timerRunning ? 'bi bi-pause-fill' : 'bi bi-play-fill';
        });
    }

    // ===== TABS =====
    document.querySelectorAll('.cp-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.cp-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const sec = document.getElementById('sec-' + tab.dataset.section);
            if (sec) {
                sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ===== CATEGORY =====
    let selectedCategory = null;
    let selectedProcedures = [];

    document.querySelectorAll('.cat-btn[data-cat]').forEach(btn => {
        btn.addEventListener('click', () => {
            if (READ_ONLY) return;
            selectedCategory = btn.dataset.cat;
            document.getElementById('cpCategory').value = selectedCategory;
            document.querySelectorAll('.cat-btn[data-cat]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderProcedures();
            triggerAutosave();
        });
    });

    function renderProcedures() {
        const container = document.getElementById('procChips');
        if (!container) return;
        const procs = PROCEDURES[selectedCategory] || [];
        if (procs.length === 0) {
            container.innerHTML = '<span class="text-muted small">Selecione uma categoria.</span>';
            return;
        }
        container.innerHTML = procs.map(p => `
            <span class="proc-chip ${selectedProcedures.includes(p) ? 'selected' : ''}" data-proc="${p}">
                ${p}
            </span>
        `).join('');
        container.querySelectorAll('.proc-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                if (READ_ONLY) return;
                const proc = chip.dataset.proc;
                if (selectedProcedures.includes(proc)) {
                    selectedProcedures = selectedProcedures.filter(x => x !== proc);
                    chip.classList.remove('selected');
                } else {
                    selectedProcedures.push(proc);
                    chip.classList.add('selected');
                }
                checkImplant();
                checkLipo();
                renderBudgetRows();
                triggerAutosave();
            });
        });
    }

    function checkImplant() {
        const show = selectedProcedures.some(p => IMPLANT_PROCS.includes(p));
        const el = document.getElementById('implantModule');
        if (el) el.style.display = show ? 'block' : 'none';
    }

    function checkLipo() {
        const show = selectedProcedures.some(p => LIPO_PROCS.includes(p));
        const el = document.getElementById('lipoAreasContainer');
        if (el) el.style.display = show ? 'block' : 'none';
    }

    // ===== INDICATION =====
    document.querySelectorAll('.indication-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (READ_ONLY) return;
            document.querySelectorAll('.indication-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('cpIndicationStatus').value = btn.dataset.val;
            triggerAutosave();
        });
    });

    // ===== LIPO AREAS =====
    let selectedLipoAreas = [];
    document.querySelectorAll('.area-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            if (READ_ONLY) return;
            const area = chip.dataset.area;
            if (selectedLipoAreas.includes(area)) {
                selectedLipoAreas = selectedLipoAreas.filter(x => x !== area);
                chip.classList.remove('selected');
            } else {
                selectedLipoAreas.push(area);
                chip.classList.add('selected');
            }
            triggerAutosave();
        });
    });

    // ===== TECHNOLOGIES =====
    let selectedTechs = [];
    document.querySelectorAll('.tech-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            if (READ_ONLY) return;
            const tech = chip.dataset.tech;
            if (selectedTechs.includes(tech)) {
                selectedTechs = selectedTechs.filter(x => x !== tech);
                chip.classList.remove('selected');
            } else {
                selectedTechs.push(tech);
                chip.classList.add('selected');
            }
            triggerAutosave();
        });
    });

    // ===== BUDGET =====
    function renderBudgetRows() {
        const container = document.getElementById('budgetRows');
        if (!container) return;
        if (selectedProcedures.length === 0) {
            container.innerHTML = '<p class="text-muted small">Selecione procedimentos no Planejamento para gerar linhas de orçamento.</p>';
            calcTotal();
            return;
        }
        container.innerHTML = selectedProcedures.map(proc => `
            <div class="budget-row">
                <label>${proc}</label>
                <div class="input-group" style="width:180px">
                    <span class="input-group-text">R$</span>
                    <input type="number" class="form-control form-control-sm-cp budget-proc-input"
                           data-proc="${proc}" step="0.01" placeholder="0,00"
                           ${READ_ONLY ? 'readonly' : ''}>
                </div>
            </div>
        `).join('');
        container.querySelectorAll('.budget-proc-input').forEach(inp => {
            inp.addEventListener('input', () => {
                calcTotal();
                triggerAutosave();
            });
        });
        calcTotal();
    }

    function calcTotal() {
        let total = 0;
        document.querySelectorAll('.budget-proc-input').forEach(inp => {
            total += parseFloat(inp.value) || 0;
        });
        const allIn = parseFloat(document.getElementById('cpAllIn')?.value) || 0;
        total += allIn;
        const display = document.getElementById('cpTotalDisplay');
        if (display) display.textContent = 'R$ ' + total.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
    }

    const allInInput = document.getElementById('cpAllIn');
    if (allInInput) {
        allInInput.addEventListener('input', () => { calcTotal(); triggerAutosave(); });
    }

    // ===== AUTOSAVE =====
    function triggerAutosave() {
        if (READ_ONLY) return;
        if (autosaveTimer) clearTimeout(autosaveTimer);
        setAutosaveStatus('saving');
        autosaveTimer = setTimeout(doSave, 1800);
    }

    function setAutosaveStatus(state) {
        const el = document.getElementById('autosaveStatus');
        if (!el) return;
        if (state === 'saving') {
            el.className = 'autosave-indicator saving';
            el.textContent = '⏳ Salvando...';
        } else if (state === 'saved') {
            autosaveLastAt = new Date();
            el.className = 'autosave-indicator saved';
            el.textContent = '✅ Salvo automaticamente';
        } else if (state === 'error') {
            el.className = 'autosave-indicator';
            el.textContent = '❌ Erro ao salvar';
        }
    }

    async function doSave(finalize = false) {
        if (!encounterId) {
            await startEncounter();
        }
        if (!encounterId) return;

        const budgetItems = {};
        document.querySelectorAll('.budget-proc-input').forEach(inp => {
            const val = parseFloat(inp.value);
            if (!isNaN(val)) budgetItems[inp.dataset.proc] = val;
        });

        const payload = {
            category: document.getElementById('cpCategory')?.value || selectedCategory,
            complaint_text: document.getElementById('cpComplaintText')?.value || '',
            plan_summary_text: document.getElementById('cpPlanSummary')?.value || '',
            consultation_seconds: timerSeconds,
            status: finalize ? 'FINAL' : 'DRAFT',
            plan: {
                indication_status: document.getElementById('cpIndicationStatus')?.value || null,
                case_type: document.getElementById('cpCaseType')?.value || null,
                selected_procedures: selectedProcedures,
                lipo_areas: selectedLipoAreas,
                implant_plane: document.getElementById('cpImplantPlane')?.value || '',
                implant_profile: document.getElementById('cpImplantProfile')?.value || '',
                implant_volume_min: parseInt(document.getElementById('cpImplantVolMin')?.value) || null,
                implant_volume_max: parseInt(document.getElementById('cpImplantVolMax')?.value) || null,
                technologies: selectedTechs,
                internacao: document.getElementById('cpInternacao')?.value || '',
                estimated_time: document.getElementById('cpEstimatedTime')?.value || '',
                follow_up_deadline: document.getElementById('cpFollowUpDeadline')?.value || '',
                reception_obs: document.getElementById('cpReceptionObs')?.value || '',
            },
            budget: {
                items: budgetItems,
                all_in_price: parseFloat(document.getElementById('cpAllIn')?.value) || null,
                currency: 'BRL'
            }
        };

        try {
            const resp = await fetch(`/api/cp/encounter/${encounterId}/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (data.ok) {
                setAutosaveStatus('saved');
            } else {
                setAutosaveStatus('error');
            }
        } catch (e) {
            console.error('Autosave error:', e);
            setAutosaveStatus('error');
        }
    }

    async function startEncounter() {
        try {
            const resp = await fetch('/api/cp/encounter/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dp_id: DP_ID, category: selectedCategory || 'FACE' })
            });
            const data = await resp.json();
            if (data.encounter_id) {
                encounterId = data.encounter_id;
            }
        } catch (e) {
            console.error('Error starting encounter:', e);
        }
    }

    // ===== LOAD EXISTING ENCOUNTER =====
    async function loadEncounter() {
        if (!encounterId) return;
        try {
            const resp = await fetch(`/api/cp/encounter/${encounterId}`);
            const data = await resp.json();

            if (data.category) {
                selectedCategory = data.category;
                document.getElementById('cpCategory').value = data.category;
                document.querySelectorAll('.cat-btn[data-cat]').forEach(b => {
                    b.classList.toggle('active', b.dataset.cat === data.category);
                });
                renderProcedures();
            }
            if (data.complaint_text) {
                const el = document.getElementById('cpComplaintText');
                if (el) el.value = data.complaint_text;
            }
            if (data.plan_summary_text) {
                const el = document.getElementById('cpPlanSummary');
                if (el) el.value = data.plan_summary_text;
            }
            if (data.consultation_seconds) {
                timerSeconds = data.consultation_seconds;
                updateTimerDisplay();
            }

            const plan = data.plan || {};
            if (plan.indication_status) {
                document.getElementById('cpIndicationStatus').value = plan.indication_status;
                document.querySelectorAll('.indication-btn').forEach(b => {
                    b.classList.toggle('active', b.dataset.val === plan.indication_status);
                });
            }
            if (plan.case_type) {
                const el = document.getElementById('cpCaseType');
                if (el) el.value = plan.case_type;
            }
            if (plan.selected_procedures && Array.isArray(plan.selected_procedures)) {
                selectedProcedures = plan.selected_procedures;
                renderProcedures();
                checkImplant();
                checkLipo();
                renderBudgetRows();
            }
            if (plan.lipo_areas && Array.isArray(plan.lipo_areas)) {
                selectedLipoAreas = plan.lipo_areas;
                document.querySelectorAll('.area-chip').forEach(chip => {
                    chip.classList.toggle('selected', selectedLipoAreas.includes(chip.dataset.area));
                });
            }
            if (plan.technologies && Array.isArray(plan.technologies)) {
                selectedTechs = plan.technologies;
                document.querySelectorAll('.tech-chip').forEach(chip => {
                    chip.classList.toggle('selected', selectedTechs.includes(chip.dataset.tech));
                });
            }
            if (plan.implant_plane) { const el = document.getElementById('cpImplantPlane'); if(el) el.value = plan.implant_plane; }
            if (plan.implant_profile) { const el = document.getElementById('cpImplantProfile'); if(el) el.value = plan.implant_profile; }
            if (plan.implant_volume_min) { const el = document.getElementById('cpImplantVolMin'); if(el) el.value = plan.implant_volume_min; }
            if (plan.implant_volume_max) { const el = document.getElementById('cpImplantVolMax'); if(el) el.value = plan.implant_volume_max; }
            if (plan.internacao) { const el = document.getElementById('cpInternacao'); if(el) el.value = plan.internacao; }
            if (plan.estimated_time) { const el = document.getElementById('cpEstimatedTime'); if(el) el.value = plan.estimated_time; }
            if (plan.follow_up_deadline) { const el = document.getElementById('cpFollowUpDeadline'); if(el) el.value = plan.follow_up_deadline; }
            if (plan.reception_obs) { const el = document.getElementById('cpReceptionObs'); if(el) el.value = plan.reception_obs; }

            const budget = data.budget || {};
            if (budget.all_in_price) { const el = document.getElementById('cpAllIn'); if(el) el.value = budget.all_in_price; }
            if (budget.items) {
                setTimeout(() => {
                    Object.entries(budget.items).forEach(([proc, val]) => {
                        const inp = document.querySelector(`.budget-proc-input[data-proc="${proc}"]`);
                        if (inp) inp.value = val;
                    });
                    calcTotal();
                }, 100);
            }

            setAutosaveStatus('saved');
        } catch (e) {
            console.error('Error loading encounter:', e);
        }
    }

    // ===== LOAD HISTORY =====
    async function loadHistory() {
        const panel = document.getElementById('historyPanel');
        if (!panel) return;
        try {
            const resp = await fetch(`/api/cp/patient/${DP_ID}/history`);
            const data = await resp.json();
            if (!Array.isArray(data) || data.length === 0) {
                panel.innerHTML = '<p class="text-muted small">Nenhuma consulta anterior encontrada.</p>';
                return;
            }
            panel.innerHTML = data.map(enc => `
                <div class="history-card" onclick="window.location.href='/api/cp/encounter/${enc.id}'">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="hc-cat">${enc.category || '—'}</span>
                        <span class="hc-date">${enc.created_at ? new Date(enc.created_at).toLocaleDateString('pt-BR') : '—'}</span>
                    </div>
                    <div class="hc-summary">${enc.complaint_text || enc.plan_summary_text || 'Sem resumo'}</div>
                    <div class="mt-1">
                        <span class="badge ${enc.status === 'FINAL' ? 'bg-success' : 'bg-warning text-dark'}">${enc.status === 'FINAL' ? 'Finalizado' : 'Rascunho'}</span>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            panel.innerHTML = '<p class="text-muted small">Erro ao carregar histórico.</p>';
        }
    }

    // ===== INPUT LISTENERS FOR AUTOSAVE =====
    ['cpComplaintText', 'cpPlanSummary', 'cpCaseType', 'cpInternacao', 'cpEstimatedTime',
     'cpFollowUpDeadline', 'cpReceptionObs', 'cpImplantPlane', 'cpImplantProfile',
     'cpImplantVolMin', 'cpImplantVolMax'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', triggerAutosave);
    });

    // Sync internacao display in retorno
    const internacaoSel = document.getElementById('cpInternacao');
    if (internacaoSel) {
        internacaoSel.addEventListener('change', () => {
            const disp = document.getElementById('retornoInternacaoDisplay');
            if (disp) {
                const map = { 'DAY_HOSPITAL': 'Day Hospital (sem pernoite)', 'OVERNIGHT': 'Com pernoite' };
                disp.textContent = map[internacaoSel.value] || '—';
            }
        });
    }

    // ===== SAVE BTN =====
    const saveBtn = document.getElementById('cpSaveBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            saveBtn.disabled = true;
            await doSave(false);
            saveBtn.disabled = false;
        });
    }

    // ===== FINALIZE BTN =====
    const finalizeBtn = document.getElementById('cpFinalizeBtn');
    if (finalizeBtn) {
        finalizeBtn.addEventListener('click', async () => {
            if (!confirm('Deseja finalizar este atendimento? Você ainda poderá editar depois.')) return;
            finalizeBtn.disabled = true;
            await doSave(true);
            finalizeBtn.disabled = false;
        });
    }

    // ===== VOICE BTN (mock) =====
    let voiceActive = false;
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => {
            voiceActive = !voiceActive;
            voiceBtn.classList.toggle('recording', voiceActive);
            const icon = document.getElementById('voiceIcon');
            if (icon) icon.className = voiceActive ? 'bi bi-mic-fill' : 'bi bi-mic';
            voiceBtn.title = voiceActive ? 'Ditado ativo (mock)' : 'Iniciar ditado de voz';
        });
    }

    // ===== EXAM / TCLE STUBS =====
    window.cpExamRequest = async function () {
        alert('Funcionalidade de Pedidos de Exame não implementada nesta versão.');
    };
    window.cpTCLE = async function () {
        alert('Funcionalidade de TCLE não implementada nesta versão.');
    };
    window.cpUploadFiles = function () {
        alert('Upload de arquivos será implementado em breve.');
    };

    // READ-ONLY: disable all inputs
    if (READ_ONLY) {
        document.querySelectorAll('input, textarea, select, button.cat-btn, .proc-chip, .area-chip, .tech-chip, .indication-btn').forEach(el => {
            if (el.tagName === 'BUTTON' || el.classList.contains('proc-chip') ||
                el.classList.contains('area-chip') || el.classList.contains('tech-chip') ||
                el.classList.contains('indication-btn')) {
                el.style.pointerEvents = 'none';
            } else {
                el.disabled = true;
            }
        });
    }

    // ===== INIT =====
    async function init() {
        startTimer();
        if (encounterId) {
            await loadEncounter();
        } else if (!READ_ONLY) {
            await startEncounter();
        }
        await loadHistory();
    }

    init();

})();
