import os
import json
import html
import calendar
import traceback
from datetime import date
from concurrent.futures import ThreadPoolExecutor
from config import now, data_extenso, SITE_URL, DIAS_CURTOS, MESES

E = lambda s: html.escape(str(s))
A = lambda u: html.escape(str(u), quote=True)
from sources.finance import coletar_financeiro
from sources.frei_gilson import meditacao_do_dia
from sources.spotify import spotify_do_dia
from sources.gmail import pendencias_do_dia, nome_remetente
from sources.google_calendar import eventos_do_dia
from sources.google_oauth import contas_disponiveis, ERROS as ERROS_GOOGLE
from sources.mercado import mercado
from sources.clima import clima_do_dia
from sources.noticias import noticias_do_dia
from sources.fe import liturgia_do_dia, santo_do_dia, feriado_proximo
from sources.util import carregar_estado, salvar_estado
from workout import treino_do_dia, mapa_muscular
from diet import dieta_do_dia
from render import pagina_html, telegram_html
from notify_telegram import enviar


# ---------- formatação ----------

def brl(v, casas=2):
    v = float(v or 0)
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-R$ " if v < 0 else "R$ ") + s


def num(v, casas=2):
    return f"{float(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def seta(var):
    if var is None:
        return "  —  "
    s = "▲" if var >= 0.05 else "▼" if var <= -0.05 else "▬"
    return f"{s}{abs(var):4.1f}%".replace(".", ",")


def _quando(dias):
    if dias < 0:
        return f"venceu há {-dias} dia" + ("s" if dias < -1 else "")
    if dias == 0:
        return "vence HOJE"
    if dias == 1:
        return "vence amanhã"
    return f"vence em {dias} dias"


def _fmt_hora(iso):
    if not iso or "T" not in iso:
        return "dia todo"
    return iso[11:16]


# ---------- blocos ----------

def _acoes_financeiras(fin):
    """Faturas/contas vencendo em até 7 dias; atrasadas viram UMA linha (provável falta de baixa no app)."""
    itens, atrasadas = [], []
    for c in fin.get("contas_a_vencer") or []:
        if c["dias"] < 0:
            atrasadas.append((c["descricao"], c["valor"]))
        else:
            itens.append((c["dias"], f'{E(c["descricao"])} — {brl(c["valor"])} ({_quando(c["dias"])})'))
    for f in fin.get("faturas_abertas") or []:
        dias = f["dias_para_vencer"]
        if dias < 0:
            atrasadas.append((f"Fatura {f['banco']}", f["valor"]))
        elif dias <= 7:
            alerta = "🔴 " if dias <= 1 else ""
            itens.append((dias, f'{alerta}Fatura {E(f["banco"])} — {brl(f["valor"])} ({_quando(dias)})'))
    itens.sort(key=lambda x: x[0])
    linhas = [t for _, t in itens]
    if atrasadas:
        total = sum(float(v) for _, v in atrasadas)
        linhas.insert(0, f"🔴 {len(atrasadas)} conta(s)/fatura(s) vencida(s) sem baixa no app — {brl(total)} "
                         f"<i>(se já pagou, marque como paga no Finance Control)</i>")
    return linhas


def _resumo_financeiro(fin):
    """Uma linha curta: próxima conta a vencer; senão, o total vencido sem baixa."""
    if not fin:
        return "Finanças indisponíveis hoje"
    futuras = sorted([(f["dias_para_vencer"], f"Fatura {f['banco']}", f["valor"])
                      for f in fin.get("faturas_abertas") or [] if 0 <= f["dias_para_vencer"] <= 7] +
                     [(c["dias"], c["descricao"], c["valor"])
                      for c in fin.get("contas_a_vencer") or [] if c["dias"] >= 0])
    if futuras:
        dias, nome, valor = futuras[0]
        return f"{E(nome)} {brl(valor)} — {_quando(dias)}"
    vencidas = [f for f in fin.get("faturas_abertas") or [] if f["dias_para_vencer"] < 0] +                [c for c in fin.get("contas_a_vencer") or [] if c["dias"] < 0]
    if vencidas:
        return f"{len(vencidas)} vencida(s) sem baixa no app ({brl(sum(float(v['valor']) for v in vencidas))})"
    return "Nenhuma conta vencendo nos próximos 7 dias"


def _bloco_financas(fin, d):
    linhas = []
    gasto = float((fin.get("mes_atual") or {}).get("despesas") or 0)
    renda = float(fin.get("renda_mensal") or 0)
    if renda > 0:
        esperado = round(d.day / calendar.monthrange(d.year, d.month)[1] * 100)
        pct = round(gasto / renda * 100)
        sinal = "⚠️" if pct > esperado + 10 else "✅"
        linhas.append(f"Gasto do mês: <b>{brl(gasto)}</b> = {pct}% da renda (ritmo esperado {esperado}%) {sinal}")
    else:
        linhas.append(f"Gasto do mês: <b>{brl(gasto)}</b>")
    ontem = fin.get("ontem") or {}
    if float(ontem.get("total_despesas") or 0) > 0:
        mg = ontem.get("maior_gasto") or {}
        extra = f' · maior: {E(mg.get("descricao", ""))} {brl(mg.get("valor"))}' if mg else ""
        linhas.append(f'Ontem: {brl(ontem["total_despesas"])}{extra}')
    if float(fin.get("saldo_total") or 0) != 0:
        linhas.append(f'Saldo em contas: {brl(fin["saldo_total"])}')
    proximas = [f for f in (fin.get("faturas_abertas") or []) if f["dias_para_vencer"] > 7]
    if proximas:
        linhas.append("Próximas faturas: " + " · ".join(
            f'{E(f["banco"])} {brl(f["valor"])} ({date.fromisoformat(f["vencimento"]).strftime("%d/%m")})'
            for f in proximas))
    return linhas


def _bloco_mercado(m):
    """Linhas para <pre> (alinhadas) + alertas de variação forte."""
    linhas, alertas = [], []
    def lin(nome, valor, var):
        linhas.append(f"{nome:<9}{valor:>13} {seta(var)}")
    if "dolar" in m:
        lin("Dólar", brl(m["dolar"]["valor"]), m["dolar"]["var"])
        if abs(m["dolar"]["var"]) >= 1:
            alertas.append(f'Dólar {seta(m["dolar"]["var"]).strip()}')
    if "euro" in m:
        lin("Euro", brl(m["euro"]["valor"]), m["euro"]["var"])
    if "ibov" in m:
        lin("Ibovespa", num(m["ibov"]["valor"], 0) + " pts", m["ibov"]["var"])
        if m["ibov"]["var"] is not None and abs(m["ibov"]["var"]) >= 2:
            alertas.append(f'Ibovespa {seta(m["ibov"]["var"]).strip()}')
    for chave, nome, un in (("boi", "Boi @", ""), ("soja", "Soja sc", ""), ("milho", "Milho sc", "")):
        if chave in m:
            lin(nome, brl(m[chave]["valor"]), m[chave]["var"])
            if m[chave]["var"] is not None and abs(m[chave]["var"]) >= 3:
                alertas.append(f'{nome.split()[0]} {seta(m[chave]["var"]).strip()}')
    if "selic" in m:
        juro_real = ""
        if "cdi" in m and "ipca12m" in m:
            juro_real = f" · real ~{num(m['cdi'] - m['ipca12m'], 1)}%"
        linhas.append(f"Selic {num(m['selic'])}% · CDI {num(m.get('cdi', 0))}%")
        if "ipca12m" in m:
            linhas.append(f"IPCA 12m {num(m['ipca12m'])}%{juro_real}")
    return linhas, alertas


def _lembretes(d):
    try:
        with open("lembretes.json", encoding="utf-8") as f:
            lista = json.load(f).get("lembretes", [])
    except (FileNotFoundError, ValueError):
        return []
    out, hoje = [], d.date()
    for l in lista:
        try:
            mes = l.get("mes") or hoje.month
            ano = hoje.year
            dia = min(int(l["dia"]), calendar.monthrange(ano, mes)[1])
            alvo = date(ano, mes, dia)
            if alvo < hoje and not l.get("mes"):            # mensal já passou: próximo mês
                mes2, ano2 = (1, ano + 1) if mes == 12 else (mes + 1, ano)
                alvo = date(ano2, mes2, min(int(l["dia"]), calendar.monthrange(ano2, mes2)[1]))
            falta = (alvo - hoje).days
            if 0 <= falta <= int(l.get("avisar_dias_antes", 3)):
                out.append((falta, f'📌 {E(l["nome"])} — {_quando(falta)} ({alvo.strftime("%d/%m")})'))
        except Exception:
            continue
    return [t for _, t in sorted(out)]


def _dieta_destaque(dieta):
    """O que muda no dia: carbo do almoço/jantar, proteína e frutas."""
    almoco, jantar = dieta["almoco"][0].split(":")[0], dieta["jantar"][0].split(":")[0]
    prot = dieta["almoco"][2].split(":")[0]
    frutas = f'{dieta["cafe"][2].split(":")[0]}/{dieta["lanche"][1].split(":")[0]}'
    return f"{almoco} no almoço · {jantar} no jantar · {prot} · frutas: {frutas}".lower().capitalize()


# ---------- coleta ----------

def _rodar(nome, fn, *args):
    try:
        return nome, fn(*args), None
    except Exception as e:
        traceback.print_exc()
        return nome, None, str(e)[:80]


def main():
    d = now()
    estado = carregar_estado()

    tarefas = {
        "Finanças": (coletar_financeiro,),
        "Meditação": (meditacao_do_dia,),
        "Spotify": (spotify_do_dia,),
        "Agenda": (eventos_do_dia,),
        "Gmail": (pendencias_do_dia,),
        "Mercado": (mercado, estado),
        "Clima": (clima_do_dia,),
        "Notícias": (noticias_do_dia, estado, d),
        "Liturgia": (liturgia_do_dia,),
        "Santo": (santo_do_dia, d),
        "Feriado": (feriado_proximo, d),
    }
    with ThreadPoolExecutor(max_workers=8) as pool:
        res = {n: (v, err) for n, v, err in
               pool.map(lambda kv: _rodar(kv[0], *kv[1]), tarefas.items())}

    val = lambda n: res[n][0]
    fontes = {}  # nome -> None (ok) ou motivo
    for n in ("Finanças", "Clima", "Liturgia"):
        fontes[n] = res[n][1]
    mer, mer_erros = val("Mercado") or ({}, [res["Mercado"][1]] if res["Mercado"][1] else [])
    fontes["Mercado"] = "; ".join(mer_erros) or None
    nots, nots_erros = val("Notícias") or ([], [res["Notícias"][1]] if res["Notícias"][1] else [])
    fontes["Notícias"] = ("; ".join(nots_erros) if not nots else None)
    if res["Spotify"][1]:
        fontes["Spotify"] = res["Spotify"][1]
    contas = contas_disponiveis()
    for servico in ("Agenda", "Gmail"):
        for conta in contas:
            rotulo = f"{servico} {'CampoFort' if conta == 'campofort' else conta}"
            fontes[rotulo] = ERROS_GOOGLE.get(rotulo)
    if not contas:
        fontes["Google"] = "sem credenciais"

    fin = val("Finanças")
    med = val("Meditação") or {"titulo": "Meditação do dia",
                               "url": "https://www.youtube.com/@FreiGilsonSomdoMonteOFICIAL/videos"}
    eventos, emails = val("Agenda") or [], val("Gmail") or []
    clima = val("Clima")
    treino, dieta = treino_do_dia(d), dieta_do_dia(d)

    # Ações: o que pede atitude hoje
    acoes = _acoes_financeiras(fin) if fin else []
    acoes += _lembretes(d)
    for ev in eventos:
        acoes.append(f'🗓️ {_fmt_hora(ev["inicio"])} — {E(ev["titulo"])} ({E(ev["conta"])})')

    mercado_linhas, alertas = _bloco_mercado(mer)
    if clima and clima["alertas"]:
        alertas.insert(0, "Clima: " + ", ".join(clima["alertas"]))
    fer = val("Feriado")
    if fer:
        quando = "hoje" if fer["faltam"] == 0 else "amanhã" if fer["faltam"] == 1 else f'em {fer["faltam"]} dias'
        alertas.append(f'Feriado {fer["nome"]} {quando}')

    # Em 10 segundos
    dez = [f'🏋️ {E(treino["nome"])} ({E(treino["dur"])})']
    dez.append("💳 " + _resumo_financeiro(fin))
    if clima:
        c = f'{clima["emoji"]} {clima["min"]}°→{clima["max"]}° · chuva {clima["chuva_pct"]}%'
        if clima["janela"]:
            c += f' · janela seca {clima["janela"]}'
        dez.append(c)
    if "dolar" in mer:
        x = f'💵 Dólar {brl(mer["dolar"]["valor"])} {seta(mer["dolar"]["var"]).strip()}'
        if "boi" in mer:
            x += f' · 🐂 @ {brl(mer["boi"]["valor"])}'
        dez.append(x)

    lit, santo = val("Liturgia"), val("Santo")
    fe = []
    if lit:
        fe.append(f'{E(lit["tempo"])} · cor {E(lit["cor"]).lower()}'
                  + (f' · Evangelho {E(lit["evangelho"])}' if lit.get("evangelho") else ""))
    if santo:
        fe.append(f"Santo do dia: {E(santo)}")

    ok = [n for n, err in fontes.items() if err is None]
    falhas = [(n, err) for n, err in fontes.items() if err is not None]
    for n, err in falhas:
        print(f"::warning::Fonte com problema — {n}: {err}")

    ctx = {
        "cabecalho": f"{DIAS_CURTOS[d.weekday()]}, {d.day} {MESES[d.month - 1][:3]}",
        "alertas": alertas, "dez": dez, "acoes": acoes,
        "financas": _bloco_financas(fin, d) if fin else [],
        "mercado": mercado_linhas, "noticias": nots,
        "emails": [{"de": nome_remetente(e["de"]), "conta": e["conta"], "assunto": e["assunto"]} for e in emails],
        "fe": fe, "meditacao": med, "clima": clima,
        "treino": treino, "mapa": mapa_muscular(treino["alvos"]),
        "dieta": dieta, "dieta_destaque": _dieta_destaque(dieta),
        "spotify": val("Spotify"),
        "fontes_ok": ok, "fontes_falha": falhas, "site": SITE_URL,
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(pagina_html(ctx))

    botoes = [[{"text": "🍽️ Dieta", "url": SITE_URL + "#dieta"},
               {"text": "🏋️ Treino", "url": SITE_URL + "#treino"}],
              [{"text": "🌐 Página completa", "url": SITE_URL}]]
    enviar(telegram_html(ctx), botoes)
    salvar_estado(estado)   # só depois do envio: notícias enviadas não se repetem
    print("OK:", data_extenso(d), "| fontes ok:", ok, "| falhas:", falhas)


if __name__ == "__main__":
    main()
