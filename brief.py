import os
import html
import traceback
from config import now, data_extenso

E = lambda s: html.escape(str(s))
A = lambda u: html.escape(str(u), quote=True)
from sources.finance import coletar_financeiro
from sources.frei_gilson import meditacao_do_dia
from sources.spotify import spotify_do_dia
from sources.gmail import pendencias_do_dia
from sources.google_calendar import eventos_do_dia
from workout import treino_do_dia, mapa_muscular
from render import pagina_html, telegram_html
from notify_telegram import enviar


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


def main():
    d = now()

    try:
        fin = coletar_financeiro()
    except Exception:
        traceback.print_exc()
        fin = {"alertas": [], "status": None}

    try:
        med = meditacao_do_dia()
    except Exception:
        traceback.print_exc()
        med = {"titulo": "Meditação do dia",
               "url": "https://www.youtube.com/@FreiGilsonSomdoMonteOFICIAL/videos"}

    try:
        sp = spotify_do_dia()
    except Exception:
        traceback.print_exc()
        sp = None

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

    treino = treino_do_dia(d)
    mapa = mapa_muscular(treino["alvos"])

    precisa_html, precisa_txt = [], []
    for al in fin.get("alertas", []):
        quando = "amanhã" if al["dias"] == 1 else f'em {al["dias"]} dias'
        precisa_html.append((len(precisa_html) + 1,
            f'<a href="{A(os.environ.get("FINANCE_URL", "#"))}">Fatura {E(al["banco"])} fecha {quando}</a> — "{E(al["texto"])}".'))
        precisa_txt.append(f'{len(precisa_txt) + 1}. <a href="{A(os.environ.get("FINANCE_URL", "#"))}">'
                           f'Fatura {E(al["banco"])} fecha {quando}</a> — "{E(al["texto"])}".')
    for ev in eventos:
        precisa_html.append((len(precisa_html) + 1,
            f'{_fmt_hora(ev["inicio"])} — {E(ev["titulo"])} ({E(ev["conta"])})'))
        precisa_txt.append(f'{len(precisa_txt) + 1}. {_fmt_hora(ev["inicio"])} — {E(ev["titulo"])} ({E(ev["conta"])})')
    for em in emails:
        precisa_html.append((len(precisa_html) + 1,
            f'E-mail de {E(em["de"])} ({E(em["conta"])}) — "{E(em["assunto"])}"'))
        precisa_txt.append(f'{len(precisa_txt) + 1}. E-mail de {E(em["de"])} ({E(em["conta"])}) — "{E(em["assunto"])}"')

    hl, hl_curta = headline(tem_agenda=bool(eventos))

    ctx = {
        "headline": hl, "headline_curta": hl_curta,
        "precisa": precisa_html, "precisa_txt": precisa_txt,
        "meditacao": med, "treino": treino, "mapa": mapa, "spotify": sp,
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(pagina_html(ctx))

    enviar(telegram_html(ctx))
    print("OK:", data_extenso(d))


if __name__ == "__main__":
    main()
