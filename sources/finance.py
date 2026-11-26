"""Finanças reais: chama a função SQL `resumo_matinal` do Supabase do Finance Control.

A função só responde com a senha própria (FINANCE_BRIEF_KEY) e devolve um JSON pronto
(faturas abertas, contas a vencer, mês atual, ontem, saldos, limites, metas).
Substitui a raspagem com Playwright, que só enxergava a tela de login."""
import os
import requests

def coletar_financeiro():
    url = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    anon = os.environ.get("SUPABASE_ANON_KEY")
    chave = os.environ.get("FINANCE_BRIEF_KEY")
    if not (url and anon and chave):
        raise RuntimeError("secrets SUPABASE_URL/SUPABASE_ANON_KEY/FINANCE_BRIEF_KEY não configurados")
    # Mensagens de erro nunca repetem o valor dos secrets (elas aparecem no Telegram).
    if not (url.startswith("https://") and url.endswith(".supabase.co")):
        raise RuntimeError("SUPABASE_URL inválida: deve ser https://<id>.supabase.co")
    if not (anon.startswith("sb_publishable_") or anon.startswith("eyJ")):
        raise RuntimeError("SUPABASE_ANON_KEY inválida: use a chave publicável")
    try:
        r = requests.post(
            f"{url}/rest/v1/rpc/resumo_matinal",
            json={"p_chave": chave},
            # Chave nova (sb_publishable_...) vai só no apikey; a legada (JWT eyJ...) também no Bearer.
            headers={"apikey": anon, **({"Authorization": "Bearer " + anon} if anon.startswith("eyJ") else {})},
            timeout=20,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Supabase inacessível ({type(e).__name__})") from None
    if r.status_code in (401, 403):
        raise RuntimeError("chave recusada (confira FINANCE_BRIEF_KEY e SUPABASE_ANON_KEY)")
    if r.status_code >= 400:
        raise RuntimeError(f"Supabase respondeu HTTP {r.status_code}")
    return r.json()
