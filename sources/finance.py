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
    r = requests.post(
        f"{url}/rest/v1/rpc/resumo_matinal",
        json={"p_chave": chave},
        headers={"apikey": anon, "Authorization": "Bearer " + anon},
        timeout=20,
    )
    if r.status_code in (401, 403):
        raise RuntimeError("chave recusada")
    r.raise_for_status()
    return r.json()
