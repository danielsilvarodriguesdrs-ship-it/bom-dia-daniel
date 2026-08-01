import requests
from sources.google_oauth import access_token, contas_disponiveis

LABEL_ROTULO = {"pessoal": "pessoal", "campofort": "CampoFort"}


def _pendencias_conta(conta):
    tok = access_token(conta)
    if not tok:
        return []
    h = {"Authorization": "Bearer " + tok}
    r = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers=h,
        params={"q": "in:inbox is:unread newer_than:2d -category:promotions -category:social", "maxResults": 5},
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
        except Exception:
            continue
    return todas
