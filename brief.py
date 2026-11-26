import os
import html
import calendar
import traceback
from datetime import date
from config import now, data_extenso

E = lambda s: html.escape(str(s))
A = lambda u: html.escape(str(u), quote=True)
from sources.finance import coletar_financeiro
from sources.frei_gilson import meditacao_do_dia
from sources.spotify import spotify_do_dia
from sources.gmail import pendencias_do_dia
from sources.google_calendar import eventos_do_dia
from sources.google_oauth import contas_disponiveis, ERROS as ERROS_GOOGLE
from workout import treino_do_dia, mapa_muscular
from diet import dieta_do_dia
from render import pagina_html, telegram_html
from notify_telegram import enviar


def brl(v):
    """1234.5 -> 'R$ 1.234,50'."""
    v = float(v or 0)
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-R$ " if v < 0 else "R$ ") + s


def _quando(dias):
    if dias < 0:
        return f"venceu há {-dias} dia" + ("s" if dias < -1 else "")
    if dias == 0:
        return "vence HOJE"
    if dias == 1:
        return "vence amanhã"
    return f"vence em {dias} dias"


def headline(tem_agenda):
    if not tem_agenda:
        return ("Agenda livre hoje, Daniel — dia aberto pra tocar no seu ritmo.",
                "dia aberto: agenda livre pra tocar no seu ritmo.")
    return ("Alguns marcos no dia, Daniel — o resto é seu.",
            "alguns compromissos no dia; o resto é seu.")


def _fmt_hora(iso):
    if not iso or "T" not in iso:
        return "dia todo"
    return iso[11:16]


def _acoes_financeiras(fin):
    """Itens financeiros que pedem ação: contas fixas e faturas vencendo em até 7 dias."""
    itens = []
    for c in fin.get("contas_a_vencer") or []:
        alerta = "🔴 " if c["dias"] <= 0 else ""
        itens.append((c["dias"], f'{alerta}{E(c["descricao"])} — {brl(c["valor"])} ({_quando(c["dias"])})'))
    for f in fin.get("faturas_abertas") or []:
        if f["dias_para_vencer"] <= 7:
            alerta = "🔴 " if f["dias_para_vencer"] <= 0 else ""
            itens.append((f["dias_para_vencer"],
                          f'{alerta}Fatura {E(f["banco"])} — {brl(f["valor"])} ({_quando(f["dias_para_vencer"])})'))
    itens.sort(key=lambda x: x[0])
    return [t for _, t in itens]


def _bloco_financas(fin, d):
    """Linhas do bloco 💰 (já em HTML seguro)."""
    linhas = []
    mes = fin.get("mes_atual") or {}
    gasto = float(mes.get("despesas") or 0)
    renda = float(fin.get("renda_mensal") or 0)
    dias_mes = calendar.monthrange(d.year, d.month)[1]
    esperado = round(d.day / dias_mes * 100)
    if renda > 0:
        pct = round(gasto / renda * 100)
        sinal = "⚠️" if pct > esperado + 10 else "✅"
        linhas.append(f"Gasto do mês: <b>{brl(gasto)}</b> = {pct}% da renda "
                      f"(esperado até hoje: {esperado}%) {sinal}")
    else:
        linhas.append(f"Gasto do mês: <b>{brl(gasto)}</b>")

    ontem = fin.get("ontem") or {}
    if float(ontem.get("total_despesas") or 0) > 0:
        mg = ontem.get("maior_gasto") or {}
        extra = f' · maior: {E(mg.get("descricao", ""))} {brl(mg.get("valor"))}' if mg else ""
        linhas.append(f'Ontem: {brl(ontem["total_despesas"])}{extra}')
    else:
        linhas.append("Ontem: nenhum gasto lançado")

    if fin.get("saldo_total") is not None:
        linhas.append(f'Saldo em contas: {brl(fin["saldo_total"])}')

    proximas = [f for f in (fin.get("faturas_abertas") or []) if f["dias_para_vencer"] > 7]
    if proximas:
        linhas.append("Próximas faturas: " + " · ".join(
            f'{E(f["banco"])} {brl(f["valor"])} ({date.fromisoformat(f["vencimento"]).strftime("%d/%m")})'
            for f in proximas))

    for m in (fin.get("metas") or [])[:2]:
        if m.get("pct") is not None:
            cheio = max(0, min(10, round(float(m["pct"]) / 10)))
            linhas.append(f'Meta {E(m["nome"])}: {"▓" * cheio}{"░" * (10 - cheio)} {m["pct"]:.0f}%')
    return linhas


def main():
    d = now()
    fontes = {}  # nome -> None (ok) ou motivo da falha

    try:
        fin = coletar_financeiro()
        fontes["Finanças"] = None
    except Exception as e:
        traceback.print_exc()
        fin = None
        fontes["Finanças"] = str(e)[:80]

    try:
        med = meditacao_do_dia()
    except Exception:
        traceback.print_exc()
        med = {"titulo": "Meditação do dia",
               "url": "https://www.youtube.com/@FreiGilsonSomdoMonteOFICIAL/videos"}

    try:
        sp = spotify_do_dia()
    except Exception as e:
        traceback.print_exc()
        sp = None
        fontes["Spotify"] = str(e)[:80]

    try:
        eventos = eventos_do_dia()
    except Exception:
        traceback.print_exc()
        eventos = []

    try:
        emails = pendencias_do_dia()
    except Exception:
        traceback.print_exc()
        emails = []

    contas = contas_disponiveis()
    for servico in ("Agenda", "Gmail"):
        for conta in contas:
            rotulo = f"{servico} {'CampoFort' if conta == 'campofort' else conta}"
            fontes[rotulo] = ERROS_GOOGLE.get(rotulo)
    if not contas:
        fontes["Google"] = "sem credenciais"

    treino = treino_do_dia(d)
    mapa = mapa_muscular(treino["alvos"])
    dieta = dieta_do_dia(d)

    acoes = _acoes_financeiras(fin) if fin else []
    for ev in eventos:
        acoes.append(f'{_fmt_hora(ev["inicio"])} — {E(ev["titulo"])} ({E(ev["conta"])})')
    for em in emails:
        acoes.append(f'E-mail de {E(em["de"])} ({E(em["conta"])}) — "{E(em["assunto"])}"')

    precisa_html = [(i, t) for i, t in enumerate(acoes, 1)]
    precisa_txt = [f"{i}. {t}" for i, t in enumerate(acoes, 1)]

    hl, hl_curta = headline(tem_agenda=bool(eventos))

    ok = [n for n, err in fontes.items() if err is None]
    falhas = [(n, err) for n, err in fontes.items() if err is not None]
    for n, err in falhas:
        print(f"::warning::Fonte com problema — {n}: {err}")

    ctx = {
        "headline": hl, "headline_curta": hl_curta,
        "precisa": precisa_html, "precisa_txt": precisa_txt,
        "financas": _bloco_financas(fin, d) if fin else [],
        "fontes_ok": ok, "fontes_falha": falhas,
        "meditacao": med, "treino": treino, "mapa": mapa, "spotify": sp, "dieta": dieta,
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(pagina_html(ctx))

    enviar(telegram_html(ctx))
    print("OK:", data_extenso(d), "| fontes ok:", ok, "| falhas:", falhas)


if __name__ == "__main__":
    main()
