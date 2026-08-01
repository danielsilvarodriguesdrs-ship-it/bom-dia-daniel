import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def enviar(texto_html):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }, timeout=20)
    r.raise_for_status()
    return r.json()
