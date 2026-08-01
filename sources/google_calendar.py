import requests
from config import now
from sources.google_oauth import access_token, contas_disponiveis

LABEL_ROTULO = {"pessoal": "pessoal", "campofort": "CampoFort"}


def _eventos_conta(conta, inicio, fim):
    tok = access_token(conta)
    if not tok:
        return []
    h = {"Authorization": "Bearer " + tok}
    r = requests.get(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers=h,
        params={
            "timeMin": inicio.isoformat(),
            "timeMax": fim.isoformat(),
            "singleEvents": "true",
            "orderBy": "startTime",
        },
        timeout=20,
    )
    r.raise_for_status()
    eventos = []
    for ev in r.json().get("items", []):
        inicio_ev = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date")
        eventos.append({
            "conta": LABEL_ROTULO.get(conta, conta),
            "titulo": ev.get("summary", "(sem título)"),
            "inicio": inicio_ev,
        })
    return eventos


def eventos_do_dia():
    """Retorna os eventos de hoje das agendas configuradas, ordenados por horário."""
    d = now()
    inicio = d.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = d.replace(hour=23, minute=59, second=59, microsecond=0)
    todos = []
    for conta in contas_disponiveis():
        try:
            todos.extend(_eventos_conta(conta, inicio, fim))
        except Exception:
            continue
    todos.sort(key=lambda e: e["inicio"] or "")
    return todos
