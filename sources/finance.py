import re
from playwright.sync_api import sync_playwright
from config import FINANCE_URL


def coletar_financeiro():
    """Retorna dict com alertas de fatura e contas. Robusto a SPA (React/Lovable)."""
    resultado = {"alertas": [], "contas": [], "status": None, "texto": ""}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(FINANCE_URL, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(2500)
        texto = page.inner_text("body")
        browser.close()

    resultado["texto"] = texto

    for m in re.finditer(r"Fatura\s+(.+?)\s+fecha em\s+(\d+)\s+dia", texto):
        banco, dias = m.group(1).strip(), int(m.group(2))
        resultado["alertas"].append({
            "banco": banco, "dias": dias,
            "texto": f"Fatura {banco} fecha em {dias} dia" + ("s" if dias != 1 else "")
        })

    ms = re.search(r"(Finanças\s+\w+)", texto)
    if ms:
        resultado["status"] = ms.group(1)

    resultado["alertas"].sort(key=lambda a: a["dias"])
    return resultado
