import os
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Sao_Paulo")


def now():
    return datetime.now(TZ)


TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
FINANCE_URL = os.environ.get("FINANCE_URL", "https://financecontrollopen.lovable.app")

FREI_GILSON_CHANNEL_ID = "UCbh6_TmFnAJLI56aAQeD3qw"
FREI_GILSON_LIVE = "https://www.youtube.com/@FreiGilsonSomdoMonteOFICIAL/live"

DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
        "Sexta-feira", "Sábado", "Domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
          "agosto", "setembro", "outubro", "novembro", "dezembro"]


def data_extenso(d=None):
    d = d or now()
    return f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]} de {d.year}"
