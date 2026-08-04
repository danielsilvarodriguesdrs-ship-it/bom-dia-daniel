import re
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
_TAG = re.compile(r"<[^>]+>")


def _sem_tags(texto_html):
    """Remove as tags e desfaz o escape, pra sobrar só texto legível."""
    texto = _TAG.sub("", texto_html)
    return (texto.replace("&lt;", "<").replace("&gt;", ">")
            .replace("&quot;", '"').replace("&#x27;", "'").replace("&amp;", "&"))


def enviar(texto_html):
    """Envia a mensagem em HTML. Se o Telegram rejeitar (tag/entidade malformada,
    por exemplo por causa de um caractere inesperado em algum dado dinâmico),
    reenvia como texto puro em vez de deixar o dia inteiro sem aviso nenhum."""
    r = requests.post(URL, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }, timeout=20)

    if r.status_code == 400:
        print(f"⚠️ Telegram rejeitou o HTML ({r.text}) — reenviando como texto puro")
        r = requests.post(URL, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": _sem_tags(texto_html),
            "disable_web_page_preview": True,
        }, timeout=20)

    r.raise_for_status()
    return r.json()
