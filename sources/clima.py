"""Clima do dia (Open-Meteo, sem chave) com alertas para quem trabalha no campo."""
from sources.util import get
from config import CIDADE, LAT, LON

URL = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
       "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
       "precipitation_sum,wind_gusts_10m_max,weather_code"
       "&hourly=precipitation_probability&timezone=America/Sao_Paulo&forecast_days=1")

# WMO weather_code -> (emoji, descrição)
CODIGOS = [
    (0, "☀️", "céu limpo"), (2, "🌤️", "poucas nuvens"), (3, "☁️", "nublado"),
    (48, "🌫️", "neblina"), (57, "🌦️", "garoa"), (67, "🌧️", "chuva"),
    (77, "🌨️", "granizo/neve"), (82, "🌧️", "pancadas de chuva"), (86, "🌨️", "neve"),
    (99, "⛈️", "trovoadas"),
]


def _codigo(c):
    for limite, emoji, desc in CODIGOS:
        if c <= limite:
            return emoji, desc
    return "🌡️", "—"


def _janela_seca(horas, probs):
    """Maior sequência entre 6h e 18h com chance de chuva < 30%."""
    melhor, atual = (None, None, 0), None
    for t, p in zip(horas, probs):
        h = int(t[11:13])
        if not 6 <= h <= 18:
            continue
        if p is not None and p < 30:
            atual = (atual[0], h, atual[2] + 1) if atual else (h, h, 1)
            if atual[2] > melhor[2]:
                melhor = atual
        else:
            atual = None
    if melhor[2] >= 2:
        return f"{melhor[0]}h–{melhor[1] + 1}h"
    return None


def clima_do_dia():
    j = get(URL.format(lat=LAT, lon=LON)).json()
    d = {k: v[0] for k, v in j["daily"].items()}
    emoji, desc = _codigo(d["weather_code"])
    alertas = []
    if d["precipitation_sum"] >= 20:
        alertas.append(f"chuva forte ({d['precipitation_sum']:.0f} mm)")
    if d["weather_code"] >= 95:
        alertas.append("trovoadas")
    if d["wind_gusts_10m_max"] >= 50:
        alertas.append(f"rajadas de {d['wind_gusts_10m_max']:.0f} km/h")
    if d["temperature_2m_max"] >= 35:
        alertas.append(f"calor de {d['temperature_2m_max']:.0f}°C")
    if d["temperature_2m_min"] <= 3:
        alertas.append("risco de geada")
    janela = None
    if (d["precipitation_probability_max"] or 0) >= 30:
        janela = _janela_seca(j["hourly"]["time"], j["hourly"]["precipitation_probability"])
    return {
        "cidade": CIDADE, "emoji": emoji, "desc": desc,
        "min": round(d["temperature_2m_min"]), "max": round(d["temperature_2m_max"]),
        "chuva_pct": d["precipitation_probability_max"] or 0, "chuva_mm": d["precipitation_sum"] or 0,
        "rajada": round(d["wind_gusts_10m_max"] or 0), "janela": janela, "alertas": alertas,
    }
