import os
import base64
import requests

CID = os.environ.get("SPOTIFY_CLIENT_ID")
CSE = os.environ.get("SPOTIFY_CLIENT_SECRET")
RTK = os.environ.get("SPOTIFY_REFRESH_TOKEN")


def _token():
    r = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token", "refresh_token": RTK},
        headers={"Authorization": "Basic " + base64.b64encode(f"{CID}:{CSE}".encode()).decode()})
    return r.json()["access_token"]


def spotify_do_dia():
    """Retorna dict com podcast e música, ou None se não configurado (fase 1)."""
    if not (CID and CSE and RTK):
        return None
    h = {"Authorization": "Bearer " + _token()}

    shows = requests.get("https://api.spotify.com/v1/me/shows?limit=10", headers=h).json()
    podcast = None
    items = shows.get("items", [])
    if items:
        show = items[0]["show"]
        eps = requests.get(
            f"https://api.spotify.com/v1/shows/{show['id']}/episodes?limit=1&market=BR",
            headers=h).json().get("items", [])
        if eps:
            e = eps[0]
            podcast = {"titulo": e["name"], "programa": show["name"],
                       "min": round(e["duration_ms"] / 60000),
                       "url": e["external_urls"]["spotify"]}

    saved = requests.get("https://api.spotify.com/v1/me/tracks?limit=50", headers=h).json()
    musica = None
    for it in saved.get("items", []):
        t = it["track"]
        genero = " ".join(a["name"] for a in t["artists"]).lower()
        if any(k in t["name"].lower() + genero for k in ["gospel", "worship", "country", "hino"]):
            musica = {"titulo": t["name"], "artista": t["artists"][0]["name"],
                      "url": t["external_urls"]["spotify"]}
            break
    if not musica:
        s = requests.get("https://api.spotify.com/v1/search",
                          params={"q": "country gospel animado", "type": "playlist", "limit": 1, "market": "BR"},
                          headers=h).json()
        pls = s.get("playlists", {}).get("items", [])
        if pls:
            musica = {"titulo": pls[0]["name"], "artista": "playlist",
                      "url": pls[0]["external_urls"]["spotify"]}
    return {"podcast": podcast, "musica": musica}
