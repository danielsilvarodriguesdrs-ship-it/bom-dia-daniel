import html
from config import data_extenso

INK, SOFT, CLAY, GREY = "#2E2C27", "#6B6A63", "#C6613F", "#B4B3A8"
GRASS_D, GRASS, GRASS_L, SKY = "#3E6B3A", "#5C9552", "#8FBF72", "#F3F6EC"
A = lambda u: html.escape(u, quote=True)
E = lambda s: html.escape(str(s))


def _pasto():
    """Pasto verde ondulado, com sol em terracota — horizonte de fazenda."""
    return f'''<svg viewBox="0 0 840 220" width="100%" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
<circle cx="700" cy="56" r="30" fill="{CLAY}" opacity="0.9"/>
<path d="M0 150 C 90 120 160 168 260 140 S 430 108 520 142 S 700 118 840 148 L840 220 L0 220 Z"
      fill="{GRASS_L}" opacity="0.55"/>
<path d="M0 172 C 110 142 220 190 340 160 S 520 130 620 168 S 760 146 840 170 L840 220 L0 220 Z"
      fill="{GRASS}" opacity="0.75"/>
<path d="M0 196 C 120 176 240 210 380 190 S 560 166 680 198 S 780 182 840 196 L840 220 L0 220 Z"
      fill="{GRASS_D}"/>
</svg>'''


def pagina_html(ctx):
    """ctx: dict com headline, precisa[], meditacao, treino, mapa, spotify."""
    ex_cards = ""
    for i, (nome, sr, mus, icone) in enumerate(ctx["treino"]["ex"], 1):
        ex_cards += (f'<div class="ex"><div class="ex-svg">{icone()}</div>'
                     f'<div class="ex-name"><span>{i}</span> {E(nome)}</div>'
                     f'<div class="ex-sr">{E(sr)}</div><div class="ex-mus">{E(mus)}</div></div>')
    precisa = "".join(
        f'<div class="item"><b>{n}.</b> {t}</div>' for n, t in ctx["precisa"]) \
        or '<div class="calm">Nada te trava hoje.</div>'
    return f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&display=swap" rel="stylesheet">
<title>Bom dia, Daniel!</title><style>
:root{{--bg:#FCFCFB;--wash:{SKY};--ink:{INK};--soft:{SOFT};--clay:{CLAY};--grey:{GREY};--hair:#E4E3DC;--grass:{GRASS}}}
*{{box-sizing:border-box;margin:0;padding:0}} body{{font-family:-apple-system,"Segoe UI",sans-serif;
color:var(--ink);background:var(--bg);line-height:1.5}}
.top{{background:linear-gradient(180deg,var(--wash) 0%,#E9F1DE 100%);border-bottom:1px solid #E1E1DF;overflow:hidden}}
.wrap{{max-width:860px;margin:0 auto;padding:38px 30px}}
.daydate{{font-size:13px;color:var(--soft);letter-spacing:.03em}}
.headline{{font-family:"Fraunces",Georgia,serif;font-size:44px;line-height:1.1;margin-top:10px;color:var(--ink)}}
.subtitle{{font-size:16px;color:var(--soft);margin-top:12px;max-width:520px}}
.daysummary{{font-size:14px;color:var(--grass);font-weight:650;margin-top:10px}}
.pasto{{margin-top:22px;line-height:0}}
.h{{font-size:12.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink)}}
.sec{{margin-top:34px}} .item{{margin-top:12px;font-size:15px;color:var(--soft)}}
.calm{{margin-top:12px;font-size:15px;color:var(--soft)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin-top:20px}}
.ex{{border:1px solid var(--hair);border-radius:14px;padding:12px;background:#fff;
box-shadow:0 1px 2px rgba(46,44,39,.04);transition:box-shadow .15s}}
.ex-svg{{height:104px;display:flex;align-items:center;justify-content:center}}
.ex-name{{font-size:13.5px;font-weight:650;margin-top:6px}} .ex-name span{{color:var(--clay);font-weight:700}}
.ex-sr{{font-size:13px}} .ex-mus{{font-size:11.5px;color:var(--soft)}}
a{{color:var(--ink);border-bottom:1px solid var(--clay);text-decoration:none;font-weight:600}}
footer{{margin-top:48px;padding-bottom:36px;font-size:12px;color:var(--soft)}}
@media(max-width:640px){{.headline{{font-size:32px}}}}</style></head><body>
<div class="top"><div class="wrap">
<div class="daydate">{E(data_extenso())}</div>
<h1 class="headline">Bom dia, Daniel!</h1>
<p class="subtitle">Abaixo estão suas atividades de hoje e as ações a serem desenvolvidas.</p>
<p class="daysummary">{E(ctx["headline"])}</p>
</div><div class="pasto">{_pasto()}</div></div>
<div class="wrap">
<div class="sec"><div class="h">Ações a serem feitas</div>{precisa}</div>
<div class="sec"><div class="h">Meditação do dia · Frei Gilson</div>
<div class="item"><a href="{A(ctx["meditacao"]["url"])}">{E(ctx["meditacao"]["titulo"])}</a></div></div>
<div class="sec"><div class="h">Treino do dia — {E(ctx["treino"]["nome"])}</div>
{ctx["mapa"]}<div class="grid">{ex_cards}</div></div>
<footer>Atualizado automaticamente todo dia às 03h00 (America/Sao_Paulo).</footer>
</div></body></html>'''


def telegram_html(ctx):
    """Versão compacta (<b>,<i>,<a>)."""
    he = A
    linhas = []
    linhas.append("🌱 <b>Bom dia, Daniel!</b>")
    linhas.append(E(data_extenso()) + " — " + E(ctx["headline_curta"]))
    linhas.append("")
    linhas.append("✅ <b>Ações a serem feitas</b>")
    if ctx["precisa_txt"]:
        linhas += ctx["precisa_txt"]
    else:
        linhas.append("Nada te trava hoje.")
    linhas.append("")
    linhas.append("🙏 <b>Meditação do dia</b>")
    linhas.append(f'<a href="{he(ctx["meditacao"]["url"])}">{E(ctx["meditacao"]["titulo"])}</a>')
    linhas.append("")
    linhas.append(f'🏋️ <b>Treino — {E(ctx["treino"]["nome"])}</b>')
    linhas.append(" · ".join(f'{E(n)} {E(sr)}' for n, sr, _, _ in ctx["treino"]["ex"]))
    if ctx.get("spotify"):
        sp = ctx["spotify"]
        if sp.get("podcast"):
            linhas += ["", "🎧 <b>Podcast do dia</b>",
                       f'<a href="{he(sp["podcast"]["url"])}">{E(sp["podcast"]["titulo"])}</a> · ~{sp["podcast"]["min"]} min']
        if sp.get("musica"):
            linhas += ["", "⏰ <b>Pra levantar o astral</b>",
                       f'<a href="{he(sp["musica"]["url"])}">♪ {E(sp["musica"]["titulo"])}</a>']
    return _cortar_seguro(linhas)


def _cortar_seguro(linhas, limite=4096):
    """Telegram recusa mensagem acima de 4096 caracteres. Corta por linha inteira
    (nunca no meio de uma tag), pra não gerar HTML quebrado."""
    texto = "\n".join(linhas)
    if len(texto) <= limite:
        return texto
    aviso = "\n\n… (resumo truncado, confira a página pro conteúdo completo)"
    mantidas = []
    total = len(aviso)
    for linha in linhas:
        if total + len(linha) + 1 > limite:
            break
        mantidas.append(linha)
        total += len(linha) + 1
    return "\n".join(mantidas) + aviso
