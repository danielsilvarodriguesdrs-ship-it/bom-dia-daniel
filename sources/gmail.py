import requests
from sources.google_oauth import access_token, contas_disponiveis, ERROS

import re

LABEL_ROTULO = {"pessoal": "pessoal", "campofort": "CampoFort"}

# Remetentes automáticos que não pedem ação (alertas, notificações, ofertas).
_AUTOMATICOS = re.compile(
    r"no-?reply|noreply|notifications?@|notificac|alert|ofertas|promo|newsletter|news@|"
    r"marketing|mailer|bounce|naoresponda|nao-responda|info@|contato@.*(loja|store)", re.I)


def _automatico(remetente):
    return bool(_AUTOMATICOS.search(remetente))


def nome_remetente(remetente):
    """'Fulano <f@x.com>' -> 'Fulano'; 'f@x.com' -> 'f@x.com'."""
    m = re.match(r'\s*"?([^"<]+?)"?\s*<', remetente)
    return m.group(1).strip() if m else remetente.strip()


def _pendencias_conta(conta):
    tok = access_token(conta)
    if not tok:
        return []
    h = {"Authorization": "Bearer " + tok}
    r = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers=h,
        params={"q": "in:inbox is:unread newer_than:1d category:primary", "maxResults": 15},
        timeout=20,
    )
    r.raise_for_status()
    ids = [m["id"] for m in r.json().get("messages", [])]
    pendencias = []
    for mid in ids:
        m = requests.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}",
            headers=h,
            params={"format": "metadata", "metadataHeaders": ["Subject", "From"]},
            timeout=20,
        ).json()
        headers = {h2["name"]: h2["value"] for h2 in m.get("payload", {}).get("headers", [])}
        if _automatico(headers.get("From", "")):
            continue
        if len(pendencias) >= 3:
            break
        pendencias.append({
            "conta": LABEL_ROTULO.get(conta, conta),
            "assunto": headers.get("Subject", "(sem assunto)"),
            "de": headers.get("From", ""),
        })
    return pendencias


def pendencias_do_dia():
    """Retorna lista de e-mails não lidos recentes das contas configuradas."""
    todas = []
    for conta in contas_disponiveis():
        try:
            todas.extend(_pendencias_conta(conta))
        except Exception as e:
            ERROS[f"Gmail {LABEL_ROTULO.get(conta, conta)}"] = str(e)[:80]
            continue
    return todas
