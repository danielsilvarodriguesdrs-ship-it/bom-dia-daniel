"""Até 5 manchetes por dia, de veículos reconhecidos, por tema, sem repetir manchetes dos últimos 7 dias.

Cada tema tem várias fontes; a ordem gira a cada dia para variar os veículos.
Cada manchete leva um resumo curto (para o "Ler mais" da página)."""
import re
import html
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from sources.util import get, hash_titulo, normalizar
from config import CIDADE

GN = "https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

GN_SITE = "https://news.google.com/rss/search?q=site:{site}+{q}+when:2d&hl=pt-BR&gl=BR&ceid=BR:pt-419"

# chave: (veículo, url[, regex de categoria do item — só para feeds gerais])
FONTES = {
    "oeste-agro": ("Revista Oeste", "https://revistaoeste.com/feed/", r"agro|agricultura|agropecu|pecu[aá]ria"),
    "oeste-agro-gn": ("Revista Oeste", GN_SITE.format(site="revistaoeste.com", q="agro")),
    "oeste-economia": ("Revista Oeste", "https://revistaoeste.com/categoria/economia/feed/"),
    "oeste-economia-gn": ("Revista Oeste", GN_SITE.format(site="revistaoeste.com", q="economia")),
    "uol-economia": ("UOL", "https://rss.uol.com.br/feed/economia.xml"),
    "uol-tec": ("UOL", "https://rss.uol.com.br/feed/tecnologia.xml"),
    "estadao-agro": ("Estadão", "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/agro/"),
    "estadao-economia": ("Estadão", "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/economia/"),
    "globorural": ("Globo Rural", "https://globorural.globo.com/rss/globorural/"),
    "canalrural": ("Canal Rural", "https://www.canalrural.com.br/feed/"),
    "valor": ("Valor Econômico", "https://valor.globo.com/rss/valor"),
    "gazeta-economia": ("Gazeta do Povo", "https://www.gazetadopovo.com.br/feed/rss/economia.xml"),
    "infomoney": ("InfoMoney", "https://www.infomoney.com.br/feed/"),
    "folha-mercado": ("Folha", "https://feeds.folha.uol.com.br/mercado/rss091.xml"),
    "exame": ("Exame", "https://exame.com/feed/"),
    "g1-agro": ("g1", "https://g1.globo.com/rss/g1/economia/agronegocios/"),
    "g1-tec": ("g1", "https://g1.globo.com/rss/g1/tecnologia/"),
    "gn-cidade": ("", GN.format(q=f"%22{CIDADE.replace(' ', '+')}%22+when:7d")),
    "gn-goias": ("", GN.format(q="Goi%C3%A1s+when:1d")),
}

# (tema, fontes em ordem de preferência, quantas manchetes, janela em horas, gira a ordem?)
TEMAS = [
    ("Agro", ["oeste-agro", "oeste-agro-gn", "globorural", "estadao-agro", "canalrural", "g1-agro"], 2, 30, True),
    ("Economia", ["oeste-economia", "oeste-economia-gn", "valor", "estadao-economia", "uol-economia",
                  "gazeta-economia", "infomoney", "folha-mercado"], 1, 30, True),
    ("Tecnologia", ["uol-tec", "exame", "g1-tec"], 1, 30, True),
    ("Região", ["gn-cidade", "gn-goias"], 1, 24 * 7, False),
]

BLOQUEADAS = {"ao vivo", "video", "horoscopo", "bbb", "futebol", "brasileirao", "loteria",
              "mega sena", "quina", "lotofacil", "lotomania", "dia de sorte", "sorteado",
              "jogo do", "escalacao", "palpite", "veja fotos", "podcast", "patrocinado", "publieditorial"}


def _xml(resp):
    """Tolerante a feeds imperfeitos: codificação ISO-8859-1 sem declaração (UOL),
    caracteres de controle e '&' solto (Revista Oeste)."""
    bruto = resp.content
    m = re.search(rb'encoding=["\']([\w-]+)', bruto[:200])
    if m:
        try:
            texto = bruto.decode(m.group(1).decode(), errors="replace")
        except LookupError:
            texto = bruto.decode("utf-8", errors="replace")
    else:                                   # sem declaração: UTF-8 se válido, senão Latin-1 (UOL)
        try:
            texto = bruto.decode("utf-8")
        except UnicodeDecodeError:
            texto = bruto.decode("iso-8859-1")
    texto = re.sub(r"<\?xml[^>]*\?>", "", texto).lstrip("﻿ \r\n\t")
    texto = re.sub(r"<\?xml-stylesheet[^>]*\?>", "", texto)
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", texto)
    texto = re.sub(r"&(?!#?\w+;)", "&amp;", texto)
    try:
        return ET.fromstring(texto)
    except ET.ParseError:                   # prefixo sem namespace declarado (ex.: <media:content>)
        texto = re.sub(r"<(/?)([A-Za-z_][\w.-]*):", r"<\1\2_", texto)
        texto = re.sub(r'\s[A-Za-z_][\w.-]*:[\w.-]+="[^"]*"', "", texto)
        return ET.fromstring(texto)


def _resumo(it):
    bruto = it.findtext("description") or ""
    t = html.unescape(re.sub(r"<[^>]+>", " ", bruto))
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"(The post|O post|Leia mais|Continue lendo).*$", "", t).strip()
    if len(t) > 260:
        t = t[:260].rsplit(" ", 1)[0] + "…"
    return t


def _quando(it):
    for campo in ("pubDate", "{http://purl.org/dc/elements/1.1/}date"):
        txt = it.findtext(campo)
        if not txt:
            continue
        try:
            q = parsedate_to_datetime(txt)
        except (TypeError, ValueError):
            try:
                q = datetime.fromisoformat(txt.replace("Z", "+00:00"))
            except ValueError:
                continue
        return q if q.tzinfo else q.replace(tzinfo=timezone.utc)
    return None


def _itens(chave, horas):
    veiculo, url, *filtro = FONTES[chave]
    raiz = _xml(get(url))
    limite = datetime.now(timezone.utc) - timedelta(hours=horas)
    for it in raiz.iter("item"):
        titulo = html.unescape((it.findtext("title") or "").strip())
        link = (it.findtext("link") or "").strip()
        fonte = veiculo
        if "news.google.com" in url and " - " in titulo:  # Google News: "Título - Veículo"
            titulo, f = titulo.rsplit(" - ", 1)
            fonte = veiculo or f
        quando = _quando(it)
        if quando and quando < limite:
            continue
        if filtro:
            cats = " ".join((c.text or "") for c in it.findall("category")).lower()
            if not re.search(filtro[0], cats):
                continue
        resumo = "" if "news.google.com" in url else _resumo(it)
        yield {"titulo": titulo, "link": link, "fonte": fonte, "resumo": resumo}


def noticias_do_dia(estado, d):
    enviadas = estado.setdefault("noticias", {})
    hoje = d.date().isoformat()
    corte = (d.date() - timedelta(days=7)).isoformat()
    for h in [h for h, dia in enviadas.items() if dia < corte]:
        del enviadas[h]

    total = 3 if d.weekday() == 6 else 5
    giro = d.timetuple().tm_yday
    escolhidas, vistas, erros, assuntos = [], set(), [], []
    for tema, fontes, qtd, horas, gira in TEMAS:
        if d.weekday() == 6 and tema in ("Economia", "Tecnologia"):
            continue
        if gira:
            k = giro % len(fontes)
            fontes = fontes[k:] + fontes[:k]
        pegas = 0
        por_fonte = 1 if qtd > 1 else qtd                  # variar os veículos dentro do tema
        for chave in fontes:
            if pegas >= qtd:
                break
            deste = 0
            try:
                for it in _itens(chave, horas):
                    if deste >= por_fonte:
                        break
                    palavras = " " + " ".join(normalizar(it["titulo"])) + " "
                    h = hash_titulo(it["titulo"])
                    if h in vistas or h in enviadas or any(f" {b} " in palavras for b in BLOQUEADAS):
                        continue
                    chave_assunto = {w for w in palavras.split() if len(w) > 3}
                    if any(len(chave_assunto & a) / max(1, len(chave_assunto | a)) > 0.3 for a in assuntos):
                        continue                            # mesmo assunto de outra manchete
                    vistas.add(h)
                    assuntos.append(chave_assunto)
                    escolhidas.append({**it, "tema": tema, "hash": h})
                    pegas += 1
                    deste += 1
                    if pegas >= qtd:
                        break
            except Exception as e:
                erros.append(f"{FONTES[chave][0] or chave}: {str(e)[:40]}")
    escolhidas = escolhidas[:total]
    for n in escolhidas:
        enviadas[n["hash"]] = hoje
    # Só é falha se nenhuma manchete saiu; fontes individuais fora do ar são normais.
    return escolhidas, ([] if escolhidas else erros)
