# bom-dia-daniel

Resumo matinal automático, disparado todo dia às 03h20 (America/Sao_Paulo) via GitHub Actions —
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
