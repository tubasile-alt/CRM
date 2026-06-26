# Notificações push de check-in no iPhone/PWA

## Requisitos de compatibilidade no iPhone

- iPhone com iOS 16.4 ou superior.
- O CRM precisa estar adicionado à Tela de Início.
- O usuário precisa abrir o CRM pela Tela de Início e permitir notificações.
- O ambiente precisa usar HTTPS.

## Teste manual mínimo

1. Fazer login como médico no iPhone.
2. Adicionar o CRM à Tela de Início.
3. Abrir o CRM pelo ícone da Tela de Início.
4. Clicar em **Ativar notificações neste iPhone** ou **Sincronizar neste iPhone**.
5. Clicar em **Enviar notificação de teste**.
6. Fazer o check-in de um paciente pela secretária.
7. Verificar se a notificação aparece no iPhone bloqueado.

## Configuração VAPID

- `VAPID_PUBLIC_KEY` pode ficar no ambiente público da aplicação.
- `VAPID_PRIVATE_KEY` deve ficar somente em Secrets/variáveis protegidas, nunca versionada no repositório.
- Ao rotacionar, gere um novo par VAPID e atualize `VAPID_PUBLIC_KEY` e `VAPID_PRIVATE_KEY` juntos.
- `VAPID_CLAIMS_EMAIL` deve usar o formato `mailto:email@dominio.com`, sem espaço depois de `mailto:`.
