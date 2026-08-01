import os
import traceback
from config import now, data_extenso
from sources.finance import coletar_financeiro
from sources.frei_gilson import meditacao_do_dia
from sources.spotify import spotify_do_dia
from workout import treino_do_dia, mapa_muscular
from render import pagina_html, telegram_html
from notify_telegram import enviar


def headline(fin, tem_agenda):
    if not tem_agenda:
        return ("Agenda livre hoje, Daniel — dia aberto pra tocar no seu ritmo.",
                "dia aberto: agenda livre pra tocar no seu ritmo.")
    return ("Alguns marcos no dia, Daniel — o resto é seu.",
            "alguns compromissos no dia; o resto é seu.")


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

    treino = treino_do_dia(d)
    mapa = mapa_muscular(treino["alvos"])

    precisa_html, precisa_txt = [], []
    for al in fin.get("alertas", []):
        quando = "amanhã" if al["dias"] == 1 else f'em {al["dias"]} dias'
        precisa_html.append((len(precisa_html) + 1,
            f'<a href="{os.environ.get("FINANCE_URL", "#")}">Fatura {al["banco"]} fecha {quando}</a> — "{al["texto"]}".'))
        precisa_txt.append(f'{len(precisa_txt) + 1}. <a href="{os.environ.get("FINANCE_URL", "#")}">'
                           f'Fatura {al["banco"]} fecha {quando}</a> — "{al["texto"]}".')

    hl, hl_curta = headline(fin, tem_agenda=False)

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
