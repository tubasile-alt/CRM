# Fase 0 — Auditoria de rotas

Esta fase cria a rede de segurança anterior à migração de rotas para Blueprints.
Ela não move, renomeia nem remove handlers.

## Entregas

- inventário determinístico de caminho, métodos, endpoint e Blueprint;
- detecção de colisões por `caminho + método`;
- baseline explícito das colisões preexistentes;
- importação do app em testes sem iniciar threads do APScheduler;
- dependências de desenvolvimento separadas das dependências de produção;
- workflow de CI que executa o contrato e publica o inventário JSON como artefato.

## Colisões preexistentes documentadas

1. `GET /api/patient/<int:patient_id>/surgeries`
   - `get_patient_surgeries`
   - `patient.get_patient_surgeries`
2. `POST /api/patient/<int:patient_id>/surgery`
   - `create_patient_surgery`
   - `patient.create_patient_surgery`

Essas colisões não são corrigidas nesta fase. O teste congela o estado atual para
impedir novas duplicidades e exige revisão explícita quando a consolidação for
realizada.

## Execução local

```bash
pip install -r requirements-dev.txt
pytest -q tests/test_route_contract.py
python scripts/audit_routes.py --output route-inventory.json
```

## Fora de escopo

- migração ou consolidação de rotas;
- alteração de URLs e endpoints;
- alteração de autenticação, páginas ou templates;
- criação de `extensions.py`;
- refatoração dos handlers.

A chamada de produção do scheduler e a posição do bloco `app.run()` permanecem
inalteradas neste PR. Os testes neutralizam o início do scheduler antes do import,
sem mudar o comportamento da aplicação em produção. A alteração direta desses
dois pontos deve ser feita em um commit isolado após o inventário ser validado no
CI, pois `app.py` é um arquivo grande e sensível.
