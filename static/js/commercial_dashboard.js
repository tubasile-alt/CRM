(async function () {
  const doctorFilter = document.getElementById('doctorFilter');
  const sections = {
    today: document.getElementById('todayTasks'),
    week: document.getElementById('weekTasks'),
    pending: document.getElementById('pendingTasks')
  };

  function badgeClass(status) {
    return {
      novo: 'bg-primary',
      conversado: 'bg-info text-dark',
      aguardando: 'bg-warning text-dark',
      fechado: 'bg-success',
      perdido: 'bg-danger'
    }[status] || 'bg-secondary';
  }

  function formatDate(dateLike) {
    if (!dateLike) return '-';
    const d = new Date(`${dateLike}T00:00:00`);
    if (Number.isNaN(d.getTime())) return dateLike;
    return d.toLocaleDateString('pt-BR');
  }

  function renderProcedures(task) {
    // Dados importados não têm procedures, usar planejamento do snapshot
    return '';
  }

  function cardActions(task) {
    return `
      <div class="d-flex flex-wrap gap-2 mt-2">
        <a class="btn btn-outline-primary btn-sm" href="/commercial/task/${task.id}">Abrir planejamento</a>
        <button class="btn btn-outline-success btn-sm" data-conversado="${task.id}">Marcar como conversado</button>
      </div>
    `;
  }

  function renderCards(tasks, container, variant) {
    if (!tasks.length) {
      container.innerHTML = '<div class="empty-state">Nenhuma tarefa nesta seção.</div>';
      return;
    }

    container.innerHTML = tasks.map(task => {
      const isHighPriority = task.priority === 'alta';
      const segmento = task.source_type === 'cp' ? 'CP' : 'DERM';
      const extra = variant === 'today'
        ? `<p class="mb-1"><strong>Consulta:</strong> ${formatDate(task.consultation_date)}</p>`
        : `<p class="mb-1"><strong>Último contato:</strong> ${task.last_contact_at || '-'}</p>`;
      return `
      <article class="task-card ${isHighPriority ? 'task-card-priority' : ''}">
        <div class="d-flex justify-content-between align-items-start gap-2">
          <div>
            <h3 class="h6 mb-1">${task.patient_name_snapshot}</h3>
            <p class="mb-1 text-muted">${task.doctor_name_snapshot}</p>
            <p class="mb-1"><small class="badge bg-secondary">${segmento}</small></p>
          </div>
          <span class="badge ${badgeClass(task.status)}">${task.status}</span>
        </div>
        <p class="mb-1"><strong>Orçamento:</strong> R$ ${Number(task.total_value).toFixed(2)}</p>
        <p class="mb-1"><strong>Prioridade:</strong> ${task.priority}</p>
        ${extra}
        ${cardActions(task)}
      </article>`;
    }).join('');

    container.querySelectorAll('[data-conversado]').forEach(btn => {
      btn.addEventListener('click', async () => {
        await fetch(`/commercial/api/task/${btn.dataset.conversado}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'conversado', mark_contacted: true })
        });
        loadAll();
      });
    });

    container.querySelectorAll('[data-budget-patient]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const patientId = btn.dataset.budgetPatient;
        const payload = JSON.parse(decodeURIComponent(btn.dataset.budget));
        const resp = await fetch(`/api/prontuario/${patientId}/generate-budget`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!resp.ok) return;
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        window.open(url, '_blank');
      });
    });
  }

  async function load(endpoint) {
    const doctorId = doctorFilter.value;
    const qs = doctorId ? `?doctor_id=${doctorId}` : '';
    const resp = await fetch(`/commercial/api/tasks/${endpoint}${qs}`);
    return resp.json();
  }

  async function loadAll() {
    const [today, week, pending] = await Promise.all([
      load('today'), load('week'), load('pending')
    ]);
    renderCards(today, sections.today, 'today');
    renderCards(week, sections.week, 'week');
    renderCards(pending, sections.pending, 'pending');
  }

  doctorFilter.addEventListener('change', loadAll);
  loadAll();
})();
