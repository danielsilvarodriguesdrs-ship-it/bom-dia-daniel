import html
import re
from config import data_extenso

INK, SOFT, CLAY, GREY = "#2E2C27", "#6B6A63", "#C6613F", "#B4B3A8"
GRASS_D, GRASS, GRASS_L, SKY = "#3E6B3A", "#5C9552", "#8FBF72", "#F3F6EC"
A = lambda u: html.escape(u, quote=True)
E = lambda s: html.escape(str(s))


_REFEICOES = [
    ("cafe", "Café da manhã"), ("lanche", "Lanche"), ("almoco", "Almoço"),
    ("pre_treino", "Pré-treino"), ("pos_treino", "Pós-treino"),
    ("jantar", "Jantar"), ("ceia", "Ceia"),
]


def _refeicoes_html(dieta):
    """Um card por refeição; itens 'Alimento: quantidade' viram linha com quantidade à direita."""
    blocos = ""
    for chave, nome in _REFEICOES:
        linhas = ""
        for it in dieta.get(chave) or []:
            it = str(it)
            if ":" in it and not it.startswith("("):
                alim, qtd = it.split(":", 1)
                linhas += (f'<li><span class="food">{E(alim.strip())}</span>'
                           f'<span class="qty">{E(qtd.strip())}</span></li>')
            else:
                linhas += f'<li class="note">{E(it)}</li>'
        blocos += (f'<article class="card meal"><h3 class="meal-name">{E(nome)}</h3>'
                   f'<ul class="foods">{linhas}</ul></article>')
    return blocos


def _fontes_txt(ctx):
    partes = [f"✅ {E(n)}" for n in ctx.get("fontes_ok", [])]
    partes += [f"⚠️ {E(n)} ({E(err)})" for n, err in ctx.get("fontes_falha", [])]
    return " · ".join(partes)


_RE_MERCADO = re.compile(r"^(.+?)\s{2,}(.+?)\s+([▲▼▬]\s*[\d.,]+%|—)\s*$")


def _mercado_html(linhas, fontes=None):
    """Linhas de largura fixa do mercado -> grupos (B3, CEPEA, Banco Central, Relações de troca),
    cada um com título e tabela nome | valor | variação; linhas soltas viram notas do grupo."""
    grupos, atual = [], None

    def novo_grupo(titulo):
        g = {"titulo": titulo, "rows": "", "notas": ""}
        grupos.append(g)
        return g

    for l in linhas:
        t = l.strip()
        cabeca = t.split("·")[0].strip()
        if cabeca and cabeca == cabeca.upper() and any(ch.isalpha() for ch in cabeca)                 and not _RE_MERCADO.match(t):
            atual = novo_grupo(t)
            continue
        if atual is None:
            atual = novo_grupo("")
        m = _RE_MERCADO.match(t)
        if m:
            nome, valor, var = m.groups()
            cls = "up" if var.startswith("▲") else "down" if var.startswith("▼") else "flat"
            var = re.sub(r"^([▲▼▬])\s*", r"\1 ", var)
            atual["rows"] += (f'<tr><th scope="row">{E(nome)}</th><td class="val">{E(valor)}</td>'
                              f'<td class="var {cls}">{E(var)}</td></tr>')
        else:
            atual["notas"] += f'<li>{E(t)}</li>'
    out = ""
    for g in grupos:
        out += '<div class="card flush mkt-grupo">'
        if g["titulo"]:
            out += f'<div class="mkt-titulo">{E(g["titulo"])}</div>'
        if g["rows"]:
            out += f'<table class="mkt"><tbody>{g["rows"]}</tbody></table>'
        if g["notas"]:
            out += f'<ul class="mkt-notes">{g["notas"]}</ul>'
        out += "</div>"
    if fontes:
        out += f'<p class="mkt-fontes">Fontes: {E(" · ".join(fontes))}</p>'
    return out


def _clima_html(c):
    if not c:
        return ""
    stats = [("Chuva", f'{E(c.get("chuva_pct", 0))}%'),
             ("Volume", f'{float(c.get("chuva_mm") or 0):.0f} mm'.replace(".", ",")),
             ("Rajadas", f'{E(c.get("rajada", 0))} km/h')]
    if c.get("janela"):
        stats.append(("Janela seca", E(c["janela"])))
    st = "".join(f'<div class="stat"><span class="k">{k}</span><span class="v">{v}</span></div>'
                 for k, v in stats)
    al = ""
    if c.get("alertas"):
        al = '<p class="wx-alert">Atenção: ' + E(", ".join(c["alertas"])) + '</p>'
    return f'''<section class="card wx" aria-label="Clima">
<div class="wx-top"><div><div class="eyebrow">Clima · {E(c.get("cidade", ""))}</div>
<div class="wx-desc">{E(c.get("emoji", ""))} {E(str(c.get("desc", "")).capitalize())}</div></div>
<div class="wx-temp"><span class="tmax">{E(c.get("max", ""))}°</span><span class="tmin">mín {E(c.get("min", ""))}°</span></div></div>
<div class="stats">{st}</div>{al}</section>'''


def _noticias_html(noticias):
    if not noticias:
        return '<p class="empty">Sem manchetes hoje.</p>'
    out = ""
    for n in noticias:
        link = A(n.get("link") or "#")
        resumo = (n.get("resumo") or "").strip()
        fonte = f'<span class="news-src">{E(n["fonte"])}</span>' if n.get("fonte") else ""
        corpo = f'<p class="news-sum">{E(resumo)}</p>' if resumo else ""
        out += (f'<article class="card news"><div class="news-meta"><span class="tag">{E(n.get("tema", ""))}</span>{fonte}</div>'
                f'<h3 class="news-title"><a href="{link}" target="_blank" rel="noopener">{E(n.get("titulo", ""))}</a></h3>'
                f'{corpo}<a class="more" href="{link}" target="_blank" rel="noopener">Ler mais <span aria-hidden="true">→</span></a></article>')
    return out


def _linhas(itens, numerar=False, vazio="", classe=""):
    """Lista em card com divisórias; item pode ser html ou (html, html_à_direita)."""
    if not itens:
        return f'<p class="empty">{vazio}</p>' if vazio else ""
    lis = ""
    for i, t in enumerate(itens, 1):
        t, dir_ = t if isinstance(t, tuple) else (t, "")
        n = f'<span class="num">{i}</span>' if numerar else ""
        lis += f'<li>{n}<div class="txt">{t}</div>{dir_}</li>'
    return f'<ul class="rows card flush{" " + classe if classe else ""}">{lis}</ul>'


_NAV = [("acoes", "Ações"), ("financas", "Finanças"), ("mercado", "Mercado"),
        ("noticias", "Notícias"), ("fe", "Fé"), ("treino", "Treino"), ("dieta", "Dieta")]

_CSS = """
:root{--bg:#F6F6F3;--surface:#FFFFFF;--ink:#101314;--soft:#3D4347;--muted:#646B70;--line:#E2E3DE;
--accent:#1E5B3A;--accent-ink:#FFFFFF;--accent-soft:#E6EFE8;--red:#B3261E;--red-soft:#FCEBE9;
--shadow:0 1px 2px rgba(16,19,20,.04),0 4px 16px rgba(16,19,20,.04);--nav:rgba(246,246,243,.88)}
@media (prefers-color-scheme:dark){:root{--bg:#0D0F10;--surface:#16191B;--ink:#F1F3F2;--soft:#C9CED1;
--muted:#9BA3A8;--line:#272B2E;--accent:#6CC08C;--accent-ink:#0D0F10;--accent-soft:#15261C;--red:#FF8A80;
--red-soft:#2B1615;--shadow:none;--nav:rgba(13,15,16,.86)}}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{font-family:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:17px;line-height:1.55;
color:var(--ink);background:var(--bg);font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{max-width:680px;margin:0 auto;padding:0 16px}
header.hero{padding:28px 0 20px}
.brand{font-size:14px;font-weight:600;color:var(--accent);letter-spacing:.02em}
h1{font-size:34px;line-height:1.12;font-weight:800;letter-spacing:-.025em;margin-top:6px}
.date{font-size:17px;color:var(--muted);margin-top:6px;font-weight:500}
.alerts{margin-top:18px;background:var(--red-soft);border:1px solid color-mix(in srgb,var(--red) 30%,transparent);
border-radius:14px;padding:14px 16px}
.alerts .eyebrow{color:var(--red)}
.alerts ul{list-style:none;margin-top:6px}
.alerts li{font-weight:600;color:var(--ink);padding:3px 0 3px 16px;position:relative}
.alerts li::before{content:"";position:absolute;left:0;top:.72em;width:7px;height:7px;border-radius:50%;background:var(--red)}
nav.tabs{position:sticky;top:0;z-index:10;background:var(--nav);backdrop-filter:saturate(180%) blur(12px);
-webkit-backdrop-filter:saturate(180%) blur(12px);border-bottom:1px solid var(--line)}
nav.tabs .wrap{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding-top:10px;padding-bottom:10px}
nav.tabs .wrap::-webkit-scrollbar{display:none}
nav.tabs a{flex:none;text-decoration:none;font-size:15px;font-weight:600;color:var(--soft);padding:8px 14px;
border-radius:999px;border:1px solid var(--line);background:var(--surface);white-space:nowrap}
nav.tabs a.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
main{padding-bottom:24px}
section.sec{margin-top:40px;scroll-margin-top:72px}
.sec-h{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:14px}
h2{font-size:24px;line-height:1.2;font-weight:800;letter-spacing:-.02em}
.sec-sub{font-size:15px;color:var(--muted);font-weight:500;white-space:nowrap}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:var(--shadow)}
.card.flush{padding:0;overflow:hidden}
.empty{color:var(--muted);font-size:17px;padding:4px 0}
.dez{margin-top:22px}
.dez ul{list-style:none;display:grid;gap:10px;margin-top:10px}
.dez li{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:12px;
padding:14px 16px;font-size:18px;font-weight:600;line-height:1.4;box-shadow:var(--shadow)}
.wx{margin-top:14px}
.wx-top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.wx-desc{font-size:20px;font-weight:700;margin-top:4px}
.wx-temp{text-align:right;line-height:1}
.tmax{display:block;font-size:44px;font-weight:800;letter-spacing:-.03em}
.tmin{display:block;font-size:15px;color:var(--muted);margin-top:6px;font-weight:600}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1px;background:var(--line);
border:1px solid var(--line);border-radius:12px;overflow:hidden;margin-top:16px}
.stat{background:var(--surface);padding:10px 12px}
.stat .k{display:block;font-size:13px;color:var(--muted);font-weight:600}
.stat .v{display:block;font-size:18px;font-weight:700;margin-top:2px}
.wx-alert{margin-top:12px;color:var(--red);font-weight:700}
ul.rows{list-style:none}
ul.rows li{display:flex;gap:12px;align-items:flex-start;padding:15px 18px;border-top:1px solid var(--line)}
ul.rows li:first-child{border-top:0}
ul.rows .txt{flex:1;min-width:0;overflow-wrap:anywhere}
ul.rows .txt i{color:var(--muted)}
.num{flex:none;width:28px;height:28px;border-radius:50%;background:var(--accent-soft);color:var(--accent);
font-size:14px;font-weight:800;display:inline-flex;align-items:center;justify-content:center;margin-top:-1px}
.sub-h{font-size:18px;font-weight:700;margin:24px 0 10px}
.mail .from{font-weight:700}
.mail .acct{font-size:13px;font-weight:600;color:var(--muted);border:1px solid var(--line);border-radius:6px;
padding:1px 7px;margin-left:6px;white-space:nowrap}
.mail .subj{display:block;color:var(--soft);margin-top:2px}
table.mkt{width:100%;border-collapse:collapse}
.mkt th,.mkt td{padding:14px 18px;border-top:1px solid var(--line);text-align:left;font-size:17px}
.mkt tr:first-child th,.mkt tr:first-child td{border-top:0}
.mkt th{font-weight:600;color:var(--soft)}
.mkt td.val{text-align:right;font-weight:700;white-space:nowrap}
.mkt td.var{text-align:right;font-weight:600;white-space:nowrap;width:1%;color:var(--muted);font-size:15px}
.mkt td.var.up{color:var(--accent)}
.mkt-grupo{margin-bottom:14px}
.mkt-titulo{font-size:13px;font-weight:700;letter-spacing:.06em;color:var(--accent);padding:14px 18px 4px}
.mkt-fontes{font-size:14px;color:var(--muted);margin-top:4px}
.mkt-notes{list-style:none;border-top:1px solid var(--line);background:var(--accent-soft);padding:12px 18px}
.mkt-notes li{font-size:15px;font-weight:600;color:var(--soft);padding:2px 0}
.news-list{display:grid;gap:12px}
.news-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.tag{font-size:12.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);
background:var(--accent-soft);border-radius:6px;padding:3px 8px}
.news-src{font-size:14px;color:var(--muted);font-weight:500}
.news-title{font-size:20px;line-height:1.3;font-weight:700;letter-spacing:-.01em;margin-top:10px}
.news-title a{text-decoration:none}
.news-sum{color:var(--soft);margin-top:8px}
.more{display:inline-block;margin-top:12px;font-size:16px;font-weight:700;color:var(--accent);text-decoration:none;
padding:4px 0}
.more:hover,.news-title a:hover{text-decoration:underline;text-underline-offset:3px}
.fe p+p{margin-top:8px}
.btn{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:14px;padding:14px 16px;
border-radius:12px;background:var(--accent);color:var(--accent-ink);text-decoration:none;font-weight:700;font-size:16px}
.btn small{display:block;font-size:13px;font-weight:600;opacity:.8;text-transform:uppercase;letter-spacing:.06em}
.btn.ghost{background:var(--surface);color:var(--ink);border:1px solid var(--line)}
.pill{font-size:15px;font-weight:700;color:var(--accent);background:var(--accent-soft);border-radius:999px;
padding:4px 12px;white-space:nowrap}
.lead{margin:-6px 0 14px;color:var(--soft);font-weight:600}
.ex .name{font-weight:700}
.ex .mus{display:block;font-size:15px;color:var(--muted);margin-top:1px}
.ex .sr{flex:none;font-weight:700;white-space:nowrap;text-align:right}
.highlight{background:var(--accent-soft);border-radius:14px;padding:14px 16px;font-weight:600;margin-bottom:12px;
border:1px solid color-mix(in srgb,var(--accent) 25%,transparent)}
.highlight .eyebrow{color:var(--accent);display:block;margin-bottom:2px}
.meals{display:grid;gap:12px}
.meal-name{font-size:18px;font-weight:800;letter-spacing:-.01em;padding-bottom:10px;border-bottom:1px solid var(--line)}
.foods{list-style:none}
.foods li{display:flex;justify-content:space-between;gap:14px;padding:10px 0;border-top:1px solid var(--line)}
.foods li:first-child{border-top:0}
.food{font-weight:500}
.qty{color:var(--muted);text-align:right;font-size:16px}
.foods li.note{display:block;color:var(--muted);font-size:15px;font-style:italic}
footer{margin-top:48px;padding:22px 0 40px;border-top:1px solid var(--line);font-size:14px;color:var(--muted);line-height:1.6}
footer b{color:var(--soft)}
@media (min-width:720px){h1{font-size:42px}header.hero{padding-top:44px}.meals{grid-template-columns:1fr 1fr}
.dez ul{grid-template-columns:1fr 1fr}}
"""

_JS = """<script>
(function(){var l=[].slice.call(document.querySelectorAll('nav.tabs a'));if(!('IntersectionObserver' in window))return;
var m={};l.forEach(function(a){m[a.getAttribute('href').slice(1)]=a});
var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){l.forEach(function(a){a.classList.remove('on')});
var a=m[e.target.id];if(a){a.classList.add('on');var b=a.parentNode;b.scrollLeft=a.offsetLeft-(b.clientWidth-a.offsetWidth)/2}}})},{rootMargin:'-80px 0px -70% 0px'});
Object.keys(m).forEach(function(id){var s=document.getElementById(id);if(s)o.observe(s)})})();
</script>"""


def _secao(id_, titulo, corpo, sub=""):
    sub = f'<span class="sec-sub">{sub}</span>' if sub else ""
    return (f'<section class="sec" id="{id_}"><div class="sec-h"><h2>{titulo}</h2>{sub}</div>'
            f'{corpo}</section>')


def pagina_html(ctx):
    """Página completa (GitHub Pages): mobile first, sem ilustrações, claro/escuro automático."""
    # Topo
    alertas = ""
    if ctx.get("alertas"):
        alertas = ('<div class="alerts" role="alert"><div class="eyebrow">Alertas de hoje</div><ul>'
                   + "".join(f'<li>{E(a)}</li>' for a in ctx["alertas"]) + '</ul></div>')
    dez = ""
    if ctx.get("dez"):
        dez = ('<div class="dez"><div class="eyebrow">Em 10 segundos</div><ul>'
               + "".join(f'<li>{x}</li>' for x in ctx["dez"]) + '</ul></div>')

    # Ações + e-mails
    acoes = _linhas(ctx.get("acoes"), numerar=True, vazio="Nada pendente hoje.")
    if ctx.get("emails"):
        mails = [f'<span class="from">{E(e["de"])}</span><span class="acct">{E(e["conta"])}</span>'
                 f'<span class="subj">{E(e["assunto"])}</span>' for e in ctx["emails"]]
        acoes += '<h3 class="sub-h">E-mails para ler</h3>' + _linhas(mails, classe="mail")
    n_acoes = len(ctx.get("acoes") or [])

    fin = _linhas(ctx.get("financas"), vazio="Finanças indisponíveis hoje.")
    mer = _mercado_html(ctx["mercado"], ctx.get("mercado_fontes")) if ctx.get("mercado") else '<p class="empty">Cotações indisponíveis hoje.</p>'
    nots = f'<div class="news-list">{_noticias_html(ctx.get("noticias"))}</div>'

    # Fé + meditação + podcast
    fe = "".join(f'<p>{x}</p>' for x in ctx.get("fe") or [])
    med = ctx.get("meditacao") or {}
    if med.get("url"):
        fe += (f'<a class="btn" href="{A(med["url"])}" target="_blank" rel="noopener"><span><small>Meditação do dia · Frei Gilson</small>'
               f'{E(med.get("titulo", ""))}</span><span aria-hidden="true">▶</span></a>')
    sp = (ctx.get("spotify") or {}).get("podcast")
    if sp:
        fe += (f'<a class="btn ghost" href="{A(sp["url"])}" target="_blank" rel="noopener"><span><small>Podcast · {E(sp.get("min", ""))} min</small>'
               f'{E(sp.get("titulo", ""))}</span><span aria-hidden="true">→</span></a>')
    fe = f'<div class="card fe">{fe}</div>' if fe else '<p class="empty">Sem conteúdo hoje.</p>'

    # Treino
    t = ctx["treino"]
    ex = []
    for nome, sr, mus, *_ in t["ex"]:
        sr_txt = "" if str(sr).strip() in ("", "-", "—") else f'<span class="sr">{E(sr)}</span>'
        ex.append((f'<span class="name">{E(nome)}</span><span class="mus">{E(mus)}</span>', sr_txt))
    treino = _linhas(ex, numerar=True, classe="ex")

    # Dieta
    dest = ctx.get("dieta_destaque")
    dieta = (f'<div class="highlight"><span class="eyebrow">Hoje muda</span>{E(dest)}</div>' if dest else "")
    dieta += f'<div class="meals">{_refeicoes_html(ctx["dieta"])}</div>'

    nav = "".join(f'<a href="#{i}">{n}</a>' for i, n in _NAV)
    return f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F6F6F3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0D0F10" media="(prefers-color-scheme: dark)">
<title>Bom dia, Daniel · {E(ctx.get("cabecalho", ""))}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{_CSS}</style></head><body>
<header class="hero"><div class="wrap">
<div class="brand">Resumo matinal</div>
<h1>Bom dia, Daniel</h1>
<div class="date">{E(ctx.get("cabecalho") or data_extenso())}</div>
{alertas}{dez}{_clima_html(ctx.get("clima"))}
</div></header>
<nav class="tabs" aria-label="Seções"><div class="wrap">{nav}</div></nav>
<main class="wrap">
{_secao("acoes", "Ações", acoes, f"{n_acoes} pendente(s)" if n_acoes else "")}
{_secao("financas", "Finanças", fin)}
{_secao("mercado", "Mercado", mer)}
{_secao("noticias", "Notícias", nots, f'{len(ctx.get("noticias") or [])} manchetes' if ctx.get("noticias") else "")}
{_secao("fe", "Fé", fe)}
{_secao("treino", "Treino do dia", f'<p class="lead">{E(t["nome"])}</p>' + treino, f'<span class="pill">{E(t["dur"])}</span>')}
{_secao("dieta", "Alimentação do dia", dieta)}
<footer><b>Atualizado automaticamente todo dia às 05h30</b> (horário de Brasília).<br>Fontes: {_fontes_txt(ctx)}</footer>
</main>{_JS}</body></html>'''


def telegram_html(ctx):
    """Mensagem curta e escaneável: topo em 10 segundos, detalhes recolhidos (<blockquote expandable>)."""
    L = []
    L.append(f'☀️ <b>Bom dia, Daniel!</b> · {E(ctx["cabecalho"])}')
    if ctx["alertas"]:
        L.append("⚠️ " + E(" · ".join(ctx["alertas"])))
    L += ["", "<b>⚡ Em 10 segundos</b>"] + [f"• {x}" for x in ctx["dez"]]

    if ctx["acoes"]:
        L += ["", "<b>✅ Ações</b>"] + [f"{i}. {t}" for i, t in enumerate(ctx["acoes"], 1)]

    if ctx["financas"]:
        L += ["", "<b>💰 Finanças</b>"] + ctx["financas"]

    if ctx["mercado"]:
        L += ["", "<b>📊 Mercado</b>", "<pre>" + E(chr(10).join(ctx["mercado"])) + "</pre>"]
        if ctx.get("mercado_fontes"):
            L.append(f'<i>Fontes: {E(" · ".join(ctx["mercado_fontes"]))}</i>')

    if ctx["noticias"]:
        L += ["", "<b>📰 Manchetes</b>"]
        for n in ctx["noticias"]:
            fonte = f' <i>({E(n["fonte"])})</i>' if n["fonte"] else ""
            L.append(f'• <b>{E(n["tema"])}:</b> <a href="{A(n["link"])}">{E(n["titulo"])}</a>{fonte}')

    if ctx["emails"]:
        L += ["", "<b>📧 E-mails para ler</b>"]
        L += [f'• {E(e["de"])} ({E(e["conta"])}): {E(e["assunto"])}' for e in ctx["emails"]]

    L += ["", "<b>🙏 Fé</b>"] + ctx["fe"]
    L.append(f'<a href="{A(ctx["meditacao"]["url"])}">▶ {E(ctx["meditacao"]["titulo"])}</a>')

    t = ctx["treino"]
    L += ["", f'<blockquote expandable><b>🏋️ {E(t["nome"])}</b> · {E(t["dur"])}']
    L += [f"{i}. {E(n)} — {E(sr)}" for i, (n, sr, _, _) in enumerate(t["ex"], 1)]
    L[-1] += "</blockquote>"

    L.append(f'<blockquote expandable><b>🍽️ Dieta</b> · {E(ctx["dieta_destaque"])}')
    for chave, nome in _REFEICOES:
        L.append(f'<b>{E(nome)}:</b> ' + " + ".join(E(it) for it in ctx["dieta"][chave]))
    L[-1] += "</blockquote>"

    sp = ctx.get("spotify") or {}
    if sp.get("podcast"):
        p = sp["podcast"]
        L.append(f'🎧 <a href="{A(p["url"])}">{E(p["titulo"])}</a> · {p["min"]} min')

    L += ["", f'<i>Fontes: {_fontes_txt(ctx)}</i>']
    return _cortar_seguro(L)


def _cortar_seguro(linhas, limite=4096):
    """Telegram recusa mensagem acima de 4096 caracteres. Corta por linha inteira
    (nunca no meio de uma tag), pra não gerar HTML quebrado."""
    import re
    # O limite vale para o texto visível (URLs dos links não contam).
    visivel = lambda t: len(html.unescape(re.sub(r"<[^>]+>", "", t)))
    texto = "\n".join(linhas)
    if visivel(texto) <= limite:
        return texto
    aviso = "\n\n… (resumo truncado, confira a página pro conteúdo completo)"
    mantidas = []
    total = len(aviso)
    for linha in linhas:
        if total + visivel(linha) + 1 > limite:
            break
        mantidas.append(linha)
        total += visivel(linha) + 1
    return "\n".join(mantidas) + aviso
