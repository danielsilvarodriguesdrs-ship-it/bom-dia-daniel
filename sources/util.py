"""HTTP com User-Agent, timeout e 1 nova tentativa; estado persistente entre dias."""
import os
import json
import time
import hashlib
import unicodedata
import re
import requests

UA = {"User-Agent": "Mozilla/5.0 (bom-dia-daniel)"}
ESTADO_ARQ = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state", "estado.json")


def get(url, timeout=15, tentativas=2, **kw):
    ultimo = None
    for i in range(tentativas):
        try:
            r = requests.get(url, headers=UA, timeout=timeout, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            ultimo = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"{type(ultimo).__name__} em {url.split('/')[2]}")


def carregar_estado():
    try:
        with open(ESTADO_ARQ, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def salvar_estado(estado):
    os.makedirs(os.path.dirname(ESTADO_ARQ), exist_ok=True)
    with open(ESTADO_ARQ, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=1, sort_keys=True)


def normalizar(texto):
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", t).split()


def hash_titulo(titulo):
    return hashlib.sha1(" ".join(normalizar(titulo)[:8]).encode()).hexdigest()[:12]
