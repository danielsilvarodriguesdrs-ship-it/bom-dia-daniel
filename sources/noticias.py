"""Até 5 manchetes por dia, curadas por tema, sem repetir manchetes dos últimos 7 dias."""
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from sources.util import get, hash_titulo, normalizar
from config import CIDADE

GN = "https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

# (tema, feeds, quantas manchetes, janela em horas)
TEMAS = [
    ("Agro", ["https://g1.globo.com/rss/g1/economia/agronegocios/",
              "https://globorural.globo.com/rss/globorural/",
              "https://www.canalrural.com.br/feed/"], 2, 30),
    ("Economia", ["https://g1.globo.com/rss/g1/economia/"], 1, 30),
    ("Tecnologia", ["https://g1.globo.com/rss/g1/tecnologia/",
                    GN.format(q="intelig%C3%AAncia+artificial+when:1d")], 1, 30),
    ("Região", [GN.format(q=f"%22{CIDADE.replace(' ', '+')}%22+when:7d"),
                GN.format(q="Goi%C3%A1s+when:1d")], 1, 24 * 7),
]

BLOQUEADAS = {"ao vivo", "video", "horoscopo", "bbb", "futebol", "brasileirao", "loteria",
              "mega sena", "quina", "jogo do", "escalacao", "palpite", "veja fotos", "podcast"}


def _itens(url, horas):
    raiz = ET.fromstring(get(url).content)
    limite = datetime.now(timezone.utc) - timedelta(hours=horas)
    for it in raiz.iter("item"):
        titulo = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        fonte = ""
        if "news.google.com" in url and " - " in titulo:   # Google News: "Título - Veículo"
            titulo, fonte = titulo.rsplit(" - ", 1)
        elif "g1.globo" in url:
            fonte = "g1"
        elif "canalrural" in url:
            fonte = "Canal Rural"
        elif "globorural" in url:
            fonte = "Globo Rural"
        try:
            quando = parsedate_to_datetime(it.findtext("pubDate"))
        except (TypeError, ValueError):
            quando = None
        if quando and quando.tzinfo is None:      # g1 usa "-0000" (fuso desconhecido)
            quando = quando.replace(tzinfo=timezone.utc)
        if quando and quando < limite:
            continue
        yield {"titulo": titulo, "link": link, "fonte": fonte, "quando": quando}


def noticias_do_dia(estado, d):
    enviadas = estado.setdefault("noticias", {})
    hoje = d.date().isoformat()
    corte = (d.date() - timedelta(days=7)).isoformat()
    for h in [h for h, dia in enviadas.items() if dia < corte]:
        del enviadas[h]

    total = 3 if d.weekday() == 6 else 5
    escolhidas, vistas, erros, assuntos = [], set(), [], []
    for tema, feeds, qtd, horas in TEMAS:
        if d.weekday() == 6 and tema in ("Economia", "Tecnologia"):
            continue
        pegas = 0
        por_feed = 1 if qtd > 1 and len(feeds) > 1 else qtd   # variar as fontes do tema
        for feed in feeds:
            if pegas >= qtd:
                break
            deste = 0
            try:
                for it in _itens(feed, horas):
                    if deste >= por_feed:
                        break
                    palavras = " " + " ".join(normalizar(it["titulo"])) + " "
                    h = hash_titulo(it["titulo"])
                    if h in vistas or h in enviadas or any(f" {b} " in palavras for b in BLOQUEADAS):
                        continue
                    chave = {w for w in palavras.split() if len(w) > 3}
                    if any(len(chave & a) / max(1, len(chave | a)) > 0.3 for a in assuntos):
                        continue   # mesmo assunto de uma manchete já escolhida
                    vistas.add(h)
                    assuntos.append(chave)
                    escolhidas.append({**it, "tema": tema, "hash": h})
                    pegas += 1
                    deste += 1
                    if pegas >= qtd:
                        break
            except Exception as e:
                erros.append(f"{tema}: {str(e)[:50]}")
    escolhidas = escolhidas[:total]
    for n in escolhidas:
        enviadas[n["hash"]] = hoje
    return escolhidas, erros
