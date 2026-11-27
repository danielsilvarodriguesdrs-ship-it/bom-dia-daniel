"""Painel de mercado pecuário — só fontes primárias.

- B3 (cotacao.b3.com.br): futuros de boi gordo (BGI), milho (CCM), dólar (DOL) e
  soja CME (SJC) — valor de referência = AJUSTE oficial do pregão anterior; Ibovespa.
- CEPEA/Esalq: boi gordo SP, bezerro MS, milho, soja Paranaguá (mercado físico).
- Banco Central (SGS): dólar e euro PTAX, Selic, CDI, IPCA 12 meses.
- Calculados: relações de troca (bezerro em @, sacas de milho por @) e base do boi.

Cada bloco é independente: se um falhar, os outros seguem e o erro vai para `erros`.
Variações de ajuste/CEPEA são calculadas contra o valor guardado no estado (dia anterior).
"""
import re
from datetime import date
from sources.util import get

B3_DERIV = "https://cotacao.b3.com.br/mds/api/v1/DerivativeQuotation/{}"
B3_INDICE = "https://cotacao.b3.com.br/mds/api/v1/InstrumentQuotation/{}"
IBGE_IPCA12 = "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2265/p/last%201?formato=json"
SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados/ultimos/{}?formato=json"
CEPEA = "https://www.cepea.org.br/br/widgetproduto.js.php?" + "&".join(
    f"id_indicador[]={i}" for i in (2, 8, 77, 92))
CEPEA_IDS = {"boi": "boi gordo", "bezerro": "bezerro - ms", "milho": "milho", "soja": "soja paranagu"}

MESES_B3 = "FGHJKMNQUVXZ"
MESES_ABR = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

FONTES = ["B3 (ajustes do pregão anterior)", "CEPEA/Esalq", "Banco Central (PTAX/SGS)", "IBGE (IPCA)"]


def _num(s):
    return float(str(s).replace("R$", "").replace(".", "").replace(",", ".").strip())


def _var(atual, anterior):
    return (atual / anterior - 1) * 100 if anterior else None


def venc_rotulo(symb):
    """BGIZ26 -> 'dez/26'."""
    m = re.search(r"([FGHJKMNQUVXZ])(\d{2})$", symb)
    return f"{MESES_ABR[MESES_B3.index(m.group(1))]}/{m.group(2)}" if m else symb


def _guardar(hist, chave, valor, ref):
    """Atualiza o histórico e devolve a variação contra o valor anterior distinto."""
    h = hist.get(chave, {})
    if h.get("ref") and h["ref"] != ref and h.get("valor") is not None:
        h["anterior"] = h["valor"]
    h.update({"ref": ref, "valor": valor})
    hist[chave] = h
    return _var(valor, h.get("anterior"))


def _b3_futuros(out, hist):
    """Dois vencimentos mais próximos de cada contrato (o 1º que ainda não venceu hoje)."""
    hoje = date.today().isoformat()
    contratos = {"boi": ("BGI", 2, 1.0), "milho": ("CCM", 1, 1.0),
                 "dolar_fut": ("DOL", 1, 1000.0), "soja_cme": ("SJC", 1, 1.0)}
    out["b3"] = {}
    for nome, (codigo, qtd, divisor) in contratos.items():
        j = get(B3_DERIV.format(codigo), timeout=20).json()
        ref = j.get("Msg", {}).get("dtTm", "")[:10]
        futs = [s for s in j.get("Scty", []) if s["mkt"]["cd"] == "FUT"
                and s["asset"]["AsstSummry"].get("mtrtyCode", "") > hoje
                and s["SctyQtn"].get("prvsDayAdjstmntPric")]
        futs.sort(key=lambda s: s["asset"]["AsstSummry"]["mtrtyCode"])
        lista = []
        for s in futs[:qtd]:
            ajuste = s["SctyQtn"]["prvsDayAdjstmntPric"] / divisor
            lista.append({"symb": s["symb"], "venc": venc_rotulo(s["symb"]), "ajuste": ajuste,
                          "var": _guardar(hist, "b3_" + s["symb"], ajuste, ref)})
        out["b3"][nome] = lista


def _ibov(out):
    t = get(B3_INDICE.format("IBOV"), timeout=20).json()["Trad"][0]["scty"]["SctyQtn"]
    out["ibov"] = {"valor": t["curPrc"], "var": t.get("prcFlcn")}


def _bcb(out):
    """Cada série isolada, com nova tentativa: o SGS às vezes responde vazio."""
    import time

    def serie(n, k=1):
        for tentativa in range(3):
            try:
                s = get(SGS.format(n, k), timeout=20).json()
                if s:
                    return s
            except ValueError:
                pass
            time.sleep(2 * (tentativa + 1))
        raise RuntimeError(f"série {n} vazia")

    falhas = []
    for chave, n in (("ptax", 1), ("euro", 21619)):
        try:
            s = serie(n, 2)
            out[chave] = {"valor": float(s[-1]["valor"]), "data": s[-1]["data"],
                          "var": _var(float(s[-1]["valor"]), float(s[-2]["valor"]))}
        except Exception:
            falhas.append(chave)
    for chave, n in (("selic", 432), ("cdi", 4389)):
        try:
            out[chave] = float(serie(n)[0]["valor"])
        except Exception:
            falhas.append(chave)
    try:                                    # IPCA 12m: fonte primária é o IBGE (SIDRA, tabela 1737)
        j = get(IBGE_IPCA12, timeout=30).json()
        out["ipca12m"] = float(j[1]["V"])
        out["ipca_ref"] = j[1]["D3N"]
    except Exception:
        try:                                # reserva: série 13522 do Banco Central
            out["ipca12m"] = float(serie(13522)[0]["valor"])
        except Exception:
            falhas.append("ipca12m")
    if falhas:
        raise RuntimeError("sem " + ", ".join(falhas))


def _cepea(out, hist):
    txt = get(CEPEA).text
    corpo = txt[txt.find("<tbody>"):txt.find("</tbody>")]
    out["cepea"] = {}
    for linha in re.findall(r"<tr>(.*?)</tr>", corpo, re.S):
        cel = [" ".join(re.sub(r"<[^>]+>", " ", c).split())
               for c in re.findall(r"<td[^>]*>(.*?)</td>", linha, re.S)]
        if len(cel) < 3:
            continue
        data, produto, valor = cel[0], cel[1].lower(), _num(cel[2])
        chave = next((k for k, v in CEPEA_IDS.items() if produto.startswith(v)), None)
        if chave:
            out["cepea"][chave] = {"valor": valor, "data": data,
                                   "var": _guardar(hist, "cepea_" + chave, valor, data)}


def _derivados(out):
    c = out.get("cepea", {})
    if "boi" in c and "bezerro" in c:
        out["troca_bezerro"] = c["bezerro"]["valor"] / c["boi"]["valor"]          # @ por bezerro
    if "boi" in c and "milho" in c:
        out["troca_milho"] = c["boi"]["valor"] / c["milho"]["valor"]              # sc de milho por @
    boi_fut = out.get("b3", {}).get("boi") or []
    if "boi" in c and boi_fut:
        out["base_boi"] = {"valor": c["boi"]["valor"] - boi_fut[0]["ajuste"], "venc": boi_fut[0]["venc"]}


def mercado(estado):
    out, erros = {}, []
    hist = estado.setdefault("mercado", {})
    for nome, fn, args in (("B3 futuros", _b3_futuros, (out, hist)), ("B3 Ibovespa", _ibov, (out,)),
                           ("Banco Central", _bcb, (out,)), ("CEPEA", _cepea, (out, hist))):
        try:
            fn(*args)
        except Exception as e:
            erros.append(f"{nome}: {str(e)[:60]}")
    _derivados(out)
    out["fontes"] = FONTES
    return out, erros
