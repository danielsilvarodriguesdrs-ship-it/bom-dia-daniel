import html
from config import data_extenso

INK, SOFT, CLAY, GREY = "#2E2C27", "#6B6A63", "#C6613F", "#B4B3A8"
A = lambda u: html.escape(u, quote=True)
E = lambda s: html.escape(str(s))


def _terreno():
    return f'''<svg viewBox="0 0 840 170" width="100%" xmlns="http://www.w3.org/2000/svg">
<path d="M118 126 a34 34 0 0 1 68 0" fill="none" stroke="{CLAY}" stroke-width="2.6"/>
<path d="M0 128 C 130 123 320 127 520 126 S 770 123 840 127" fill="none"
      stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/></svg>'''


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
<title>Resumo matinal — Daniel</title><style>
:root{{--bg:#FCFCFB;--wash:#F9F9F7;--ink:{INK};--soft:{SOFT};--clay:{CLAY};--grey:{GREY};--hair:#E4E3DC}}
*{{box-sizing:border-box;margin:0;padding:0}} body{{font-family:-apple-system,"Segoe UI",sans-serif;
color:var(--ink);background:var(--bg);line-height:1.5}}
.top{{background:var(--wash);border-bottom:1px solid #E1E1DF}} .wrap{{max-width:860px;margin:0 auto;padding:38px 30px}}
.daydate{{font-size:13px;color:var(--soft)}} .headline{{font-family:"Fraunces",Georgia,serif;font-size:40px;
line-height:1.16;margin-top:10px}} .h{{font-size:12.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}}
.sec{{margin-top:34px}} .item{{margin-top:12px;font-size:15px;color:var(--soft)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin-top:20px}}
.ex{{border:1px solid var(--hair);border-radius:12px;padding:12px;background:#fff}}
.ex-svg{{height:104px;display:flex;align-items:center;justify-content:center}}
.ex-name{{font-size:13.5px;font-weight:650;margin-top:6px}} .ex-name span{{color:var(--clay);font-weight:700}}
.ex-sr{{font-size:13px}} .ex-mus{{font-size:11.5px;color:var(--soft)}}
a{{color:var(--ink);border-bottom:1px solid var(--clay);text-decoration:none;font-weight:600}}
@media(max-width:640px){{.headline{{font-size:30px}}}}</style></head><body>
<div class="top"><div class="wrap">
<div class="daydate">{E(data_extenso())}</div>
<h1 class="headline">{E(ctx["headline"])}</h1>{_terreno()}</div></div>
<div class="wrap">
<div class="sec"><div class="h">Precisa de você</div>{precisa}</div>
<div class="sec"><div class="h">Meditação do dia · Frei Gilson</div>
<div class="item"><a href="{A(ctx["meditacao"]["url"])}">{E(ctx["meditacao"]["titulo"])}</a></div></div>
<div class="sec"><div class="h">Treino do dia — {E(ctx["treino"]["nome"])}</div>
{ctx["mapa"]}<div class="grid">{ex_cards}</div></div>
</div></body></html>'''


def telegram_html(ctx):
    """Versão compacta (<b>,<i>,<a>). & vira &amp; nos links."""
    he = lambda u: u.replace("&", "&amp;")
    linhas = []
    linhas.append("☀️ <b>Resumo matinal — Daniel</b>")
    linhas.append(E(data_extenso()) + " — " + E(ctx["headline_curta"]))
    linhas.append("")
    linhas.append("📌 <b>Precisa de você</b>")
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
    return "\n".join(linhas)[:4096]
