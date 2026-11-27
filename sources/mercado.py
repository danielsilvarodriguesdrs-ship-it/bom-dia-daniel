"""Mercado: câmbio (AwesomeAPI), Ibovespa (Yahoo), Selic/CDI/IPCA (BCB SGS) e agro (CEPEA).
Cada parte é independente: se uma falhar, as outras seguem e o erro vai para `erros`."""
import re
from sources.util import get

AWESOME = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL"
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/%5EBVSP?range=5d&interval=1d"
SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados/ultimos/1?formato=json"
CEPEA = ("https://www.cepea.org.br/br/widgetproduto.js.php"
         "?id_indicador[]=2&id_indicador[]=92&id_indicador[]=77")
CEPEA_NOMES = {"boi": "Boi Gordo", "soja": "Soja", "milho": "Milho"}


def _num(s):
    return float(str(s).replace("R$", "").replace(".", "").replace(",", ".").strip())


def _cambio(out):
    j = get(AWESOME).json()
    out["dolar"] = {"valor": float(j["USDBRL"]["bid"]), "var": float(j["USDBRL"]["pctChange"])}
    out["euro"] = {"valor": float(j["EURBRL"]["bid"]), "var": float(j["EURBRL"]["pctChange"])}


def _ibov(out):
    r = get(YAHOO).json()["chart"]["result"][0]
    closes = [c for c in r["indicators"]["quote"][0]["close"] if c is not None]
    atual = r["meta"].get("regularMarketPrice") or closes[-1]
    # fechamento anterior = penúltimo candle diário (o último é o pregão do próprio preço atual)
    anterior = closes[-2] if len(closes) >= 2 else None
    out["ibov"] = {"valor": atual, "var": (atual / anterior - 1) * 100 if anterior else None}


def _juros(out):
    for chave, serie in (("selic", 432), ("cdi", 4389), ("ipca12m", 13522)):
        out[chave] = float(get(SGS.format(serie), timeout=20).json()[0]["valor"])


def _cepea(out, estado):
    txt = get(CEPEA).text
    corpo = txt[txt.find("<tbody>"):txt.find("</tbody>")]
    linhas = re.findall(r"<tr>(.*?)</tr>", corpo, re.S)
    hist = estado.setdefault("cepea", {})
    for linha in linhas:
        cel = [re.sub(r"<[^>]+>", " ", c).split() for c in re.findall(r"<td[^>]*>(.*?)</td>", linha, re.S)]
        if len(cel) < 3:
            continue
        data, produto, valor = " ".join(cel[0]), " ".join(cel[1]).lower(), _num(" ".join(cel[2]))
        chave = "boi" if "boi" in produto else "soja" if "soja" in produto else "milho" if "milho" in produto else None
        if not chave:
            continue
        h = hist.get(chave, {})
        if h.get("data") and h["data"] != data:          # dado novo: o de ontem vira referência
            h["anterior"] = h["valor"]
        h.update({"data": data, "valor": valor})
        hist[chave] = h
        var = (valor / h["anterior"] - 1) * 100 if h.get("anterior") else None
        out[chave] = {"valor": valor, "var": var, "data": data}


def mercado(estado):
    out, erros = {}, []
    for nome, fn in (("câmbio", _cambio), ("Ibovespa", _ibov), ("juros", _juros)):
        try:
            fn(out)
        except Exception as e:
            erros.append(f"{nome}: {str(e)[:60]}")
    try:
        _cepea(out, estado)
    except Exception as e:
        erros.append(f"CEPEA: {str(e)[:60]}")
    return out, erros
