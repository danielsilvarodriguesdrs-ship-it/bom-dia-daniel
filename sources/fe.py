"""Liturgia do dia, santo do dia e feriados próximos."""
import re
from datetime import date
from sources.util import get
from config import MESES

LITURGIA = "https://liturgia.up.railway.app/"
SANTO_RSS = "https://www.vaticannews.va/pt/santo-do-dia.rss.xml"
FERIADOS = "https://brasilapi.com.br/api/feriados/v1/{}"


def liturgia_do_dia():
    j = get(LITURGIA, timeout=20).json()
    ev = j.get("evangelho") or {}
    return {"tempo": j.get("liturgia"), "cor": j.get("cor"), "evangelho": ev.get("referencia")}


def santo_do_dia(d):
    xml = get(SANTO_RSS).text
    alvo = f"- {d.day} {MESES[d.month - 1]}"
    for t in re.findall(r"<title>([^<]+)</title>", xml):
        if t.strip().endswith(alvo):
            return t.rsplit(" - ", 1)[0].strip()
    return None


def feriado_proximo(d, dias=7):
    """Próximo feriado nacional em até `dias` dias (inclui hoje)."""
    hoje = d.date()
    lista = get(FERIADOS.format(hoje.year)).json()
    if hoje.month == 12:
        try:
            lista += get(FERIADOS.format(hoje.year + 1)).json()
        except Exception:
            pass
    for f in lista:
        dia = date.fromisoformat(f["date"])
        falta = (dia - hoje).days
        if 0 <= falta <= dias:
            return {"nome": f["name"], "data": dia, "faltam": falta}
    return None
