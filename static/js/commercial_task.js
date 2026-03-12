(async function () {
  const id = window.COMMERCIAL_TASK_ID;
  const statusField = document.getElementById('statusField');
  const priorityField = document.getElementById('priorityField');
  const followupField = document.getElementById('followupField');
  const notesField = document.getElementById('notesField');
  const saveBtn = document.getElementById('saveTaskBtn');
  const waBtn = document.getElementById('taskWhatsAppBtn');
  const printBtn = document.getElementById('taskPrintBtn');

  let taskData = null;

  async function loadTask() {
    const resp = await fetch(`/commercial/api/task/${id}`);
    taskData = await resp.json();
    waBtn.href = taskData.whatsapp_templates.orcamento;
  }

  saveBtn.addEventListener('click', async () => {
    await fetch(`/commercial/api/task/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: statusField.value,
        priority: priorityField.value,
        next_followup_date: followupField.value,
        seller_notes: notesField.value
      })
    });
    alert('Ficha comercial atualizada.');
  });

  printBtn.addEventListener('click', async () => {
    if (!taskData) return;
    const payload = { procedures: taskData.procedures.map(p => ({ name: p.name, budget: p.budget_value, value: p.planned_value })) };
    const resp = await fetch(`/api/prontuario/${taskData.patient_id}/generate-budget`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) return;
    const blob = await resp.blob();
    window.open(URL.createObjectURL(blob), '_blank');
  });

  loadTask();
})();
