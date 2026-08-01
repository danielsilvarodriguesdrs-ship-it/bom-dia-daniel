import os
import requests

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

CONTAS = {
    "pessoal": os.environ.get("GOOGLE_REFRESH_TOKEN_PESSOAL"),
    "campofort": os.environ.get("GOOGLE_REFRESH_TOKEN_CAMPOFORT"),
}


def access_token(conta):
    refresh_token = CONTAS.get(conta)
    if not (CLIENT_ID and CLIENT_SECRET and refresh_token):
        return None
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }, timeout=20)
    r.raise_for_status()
    return r.json()["access_token"]


def contas_disponiveis():
    return [nome for nome, tok in CONTAS.items() if tok]
