# Análise da aba **Sales** (`/sale`)

## 1) Visão geral funcional

A aba Sales é uma tela de funil comercial restrita à usuária `marcella`, renderizada em `templates/sale.html` e alimentada principalmente pelo endpoint `/api/crm/marcella-sales-funnel`. O fluxo principal é:

1. Frontend chama `loadFunnel()` no `DOMContentLoaded`.
2. O endpoint retorna pacientes com procedimentos pendentes, status/temperatura e próximos contatos.
3. A UI renderiza KPIs, painéis de prioridade (hoje/atrasados) e cards por “temperatura” do lead.
4. No modal, a usuária atualiza status/temperatura/follow-up, que é salvo em `/api/crm/patient-funnel-status/<patient_id>`.

---

## 2) Pontos fortes

- **Boa experiência operacional**: KPIs rápidos, painéis de prioridade e atalhos de WhatsApp.
- **Modelo de trabalho orientado a ação**: modal centraliza classificação + próximo contato + tentativas.
- **Visão de valor**: total por paciente e destaque para “alto valor”.

---

## 3) Riscos e oportunidades técnicas

### 3.1 Acoplamento por nomes fixos (regra de acesso e médico)

Hoje, regras críticas dependem de *strings hardcoded*:

- Acesso permitido apenas se `current_user.username == 'marcella'`.
- Médico buscado por `User.name LIKE '%arthur%'` com papel `medico`.

**Impacto**: frágil para produção (mudança de nome/login quebra a feature), difícil de escalar para múltiplos operadores/médicos.

**Recomendação**:
- Migrar para permissão por papel/escopo (`role` + permission flags).
- Associar usuários/médicos por `id` ou relação explícita (ex.: tabela de carteira/owner).

### 3.2 Possível gargalo de performance (N+1)

No endpoint principal, para cada paciente há uma busca individual em `PatientFunnelStatus` dentro do loop de agregação.

**Impacto**: aumento de latência conforme volume de pacientes.

**Recomendação**:
- Carregar status em lote (join/subquery) e mapear em memória por `patient_id`.

### 3.3 Side effect automático em toda carga de página

Após cada `loadFunnel()` e também após salvar no modal, o frontend chama `syncToGoogleSheets()` automaticamente.

**Impacto**:
- Sobrecarga de chamadas externas.
- Possível lentidão/perda de previsibilidade (sincronização sem confirmação explícita).

**Recomendação**:
- Tornar sincronização ação explícita (botão “Sincronizar”).
- Alternativa: debounce/agendamento em background (fila).

### 3.4 Risco de XSS no frontend

A renderização usa `innerHTML` com campos vindos da API (`patient_name`, `procedure_name`, `observations`, `doctor_notes`, etc.).

**Impacto**: se algum dado chegar com HTML/JS malicioso, pode haver execução no navegador.

**Recomendação**:
- Escapar dados dinâmicos antes de interpolar HTML, ou
- Construir DOM com `textContent` nos campos textuais.

### 3.5 Filtro de ano fixo

O select de ano está fixo em 2024/2025/2026.

**Impacto**: envelhecimento da interface e manutenção manual anual.

**Recomendação**:
- Gerar anos dinamicamente (ex.: ano atual ± N).

### 3.6 Logs de debug em produção

Há `console.log` em funções críticas de renderização.

**Impacto**: ruído em produção e possível exposição de dados em ambiente compartilhado.

**Recomendação**:
- Remover logs ou encapsular em flag de debug.

---

## 4) Prioridade sugerida (quick wins)

1. **Segurança**: mitigação de XSS na renderização (`innerHTML`).
2. **Confiabilidade**: remover hardcode de usuário/médico.
3. **Performance**: eliminar N+1 no carregamento do funil.
4. **Operação**: tornar sync com Google Sheets explícito.
5. **Manutenibilidade**: ano dinâmico + limpeza de logs.

---

## 5) Conclusão

A aba Sales está funcional e orientada para conversão, com boa usabilidade para rotina comercial. O principal débito técnico está em **robustez de regras de acesso**, **segurança de renderização HTML** e **eficiência de consulta/sincronização**. Com os ajustes acima, a aba tende a ficar mais escalável, segura e previsível.
