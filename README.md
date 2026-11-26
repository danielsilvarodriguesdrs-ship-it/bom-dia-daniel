# bom-dia-daniel

Resumo matinal automático, disparado todo dia às 05h30 (America/Sao_Paulo) — cron-job.org aciona o workflow (o schedule do GitHub fica só como reserva) —
não depende do PC estar ligado. Envia mensagem no Telegram e publica uma página no GitHub Pages.

## Secrets necessários (Settings → Secrets and variables → Actions)

- `TELEGRAM_BOT_TOKEN` — token do bot (via @BotFather)
- `TELEGRAM_CHAT_ID` — id do chat que recebe as mensagens
- `FINANCE_URL` — URL do Finance Control

## Testar manualmente

Actions → bom-dia-daniel → Run workflow.

## Fase 2 (não implementado)

Agenda/Gmail (Google API) e Spotify (OAuth) — ver `sources/spotify.py` (stub, retorna `None`
se as credenciais não estiverem configuradas).
