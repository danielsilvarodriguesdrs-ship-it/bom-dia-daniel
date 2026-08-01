import requests
import xml.etree.ElementTree as ET
from config import FREI_GILSON_CHANNEL_ID, FREI_GILSON_LIVE

FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={FREI_GILSON_CHANNEL_ID}"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def meditacao_do_dia():
    """Pega o upload mais recente do canal (evangelho/meditação do dia)."""
    try:
        r = requests.get(FEED, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        entry = root.find("a:entry", NS)
        if entry is None:
            raise ValueError("feed vazio")
        title = entry.find("a:title", NS).text
        vid = entry.find("yt:videoId", NS).text
        return {
            "titulo": title,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "live": FREI_GILSON_LIVE,
        }
    except Exception:
        return {
            "titulo": "Meditação da Palavra — vídeo de hoje (Frei Gilson)",
            "url": "https://www.youtube.com/@FreiGilsonSomdoMonteOFICIAL/videos",
            "live": FREI_GILSON_LIVE,
        }
