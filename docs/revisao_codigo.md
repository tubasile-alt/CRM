# Revisão de código — CRM

Data: 2026-02-25

## Escopo revisado
- `app.py`
- `config.py`
- `routes/crm.py`
- `routes/patient.py`

---

## Achados prioritários

### 1) **Controle de acesso ausente** em atualização de planos (risco alto)
**Onde:** `routes/crm.py` em `PATCH /api/crm/records/<plan_id>`.

**Problema:** a rota exige login, mas não valida se o usuário atual é médico responsável pelo registro, admin, ou sequer se tem permissão para alterar aquele `plan_id`.

**Impacto:** um usuário autenticado pode alterar status/observações de planos de outros médicos/pacientes (violação de integridade e confidencialidade).

**Recomendação:**
- Validar ownership via `plan.note.doctor_id == current_user.id` quando médico.
- Permitir exceção somente para perfis admin explícitos.
- Retornar `403` para acessos sem autorização.

---

### 2) **Controle de acesso incompleto** ao marcar procedimento como realizado (risco alto)
**Onde:** `app.py` em `POST /api/cosmetic-plans/<plan_id>/perform`.

**Problema:** a rota apenas verifica `@login_required`; não há validação de papel (médico/admin) nem de ownership do plano.

**Impacto:** qualquer usuário autenticado pode marcar planos como realizados e gerar evolução automática no prontuário.

**Recomendação:**
- Restringir operação para médico/admin.
- Conferir vínculo com o médico dono da nota/plano.
- Registrar auditoria (quem alterou, quando, e valores antigos/novos).

---

### 3) **Open redirect** no login (risco médio)
**Onde:** `app.py` em `/login`.

**Problema:** o parâmetro `next` vindo da query string é redirecionado diretamente (`redirect(next_page ...)`) sem validação de destino.

**Impacto:** facilita phishing após login (usuário entra no sistema e é redirecionado para domínio externo malicioso).

**Recomendação:**
- Validar `next` para aceitar apenas URLs locais (mesmo host/path relativo).
- Se inválida, ignorar e redirecionar para rota interna segura (`index`).

---

### 4) **Configuração insegura por padrão** em produção (risco médio)
**Onde:** `config.py`.

**Problema:**
- `SECRET_KEY` possui fallback fixo (`dev-secret-key-change-in-production`).
- `SESSION_COOKIE_SECURE = False` por padrão.

**Impacto:**
- Chave previsível enfraquece segurança de sessão/assinaturas.
- Cookie de sessão pode trafegar em HTTP sem TLS.

**Recomendação:**
- Falhar startup em produção se `SESSION_SECRET` não estiver configurado.
- Habilitar `SESSION_COOKIE_SECURE = True` em produção.
- Considerar `SESSION_COOKIE_SAMESITE='Strict'` para áreas administrativas.

---

## Achados secundários

### 5) Exposição de mensagem interna de erro ao cliente
**Onde:** `routes/patient.py` em `get_patient_surgeries`.

**Problema:** em exceção, a API retorna `str(e)` ao cliente.

**Impacto:** vazamento de detalhes internos (stack/error text, nomes de tabela/campo, etc.).

**Recomendação:**
- Logar erro completo no servidor.
- Retornar mensagem genérica ao cliente (`Erro interno`).

### 6) Padrão de `except:` amplo e silencioso
**Onde:** `app.py` e `routes/patient.py`.

**Problema:** múltiplos blocos `except:` sem tipo específico e sem logging.

**Impacto:** encobre falhas reais, dificulta observabilidade e pode gerar inconsistência de dados.

**Recomendação:**
- Capturar exceções específicas (`ValueError`, etc.).
- Sempre registrar log estruturado com contexto.

### 7) Potencial N+1 query na listagem de cirurgias
**Onde:** `routes/patient.py` em `get_patient_surgeries`.

**Problema:** para cada cirurgia, busca evoluções em consulta separada.

**Impacto:** degradação de desempenho com crescimento de volume.

**Recomendação:**
- Usar eager loading (`joinedload/subqueryload`) ou consulta agregada única.

---

## Próximos passos sugeridos
1. Corrigir imediatamente os 2 itens de autorização (achados 1 e 2).
2. Endurecer fluxo de login contra open redirect (achado 3).
3. Ajustar defaults de segurança em `config.py` (achado 4).
4. Melhorar tratamento de erro e observabilidade (achados 5 e 6).
5. Refatorar endpoint de cirurgias para evitar N+1 (achado 7).
