"""Renova o acesso do Bom dia Daniel ao Google (Agenda + Gmail) de uma conta.

Uso (no terminal, dentro da pasta do projeto):
    python tools/renovar_google.py pessoal
    python tools/renovar_google.py campofort

O que faz:
 1. Pede o Client ID e o Client Secret do Google (digitados aqui, nada vai para o chat).
 2. Abre o navegador para você entrar na conta Google certa e autorizar (só leitura).
 3. Grava o novo token direto no GitHub como secret, usando o `gh` já logado.
Usa o cliente "Bom dia Daniel!" (Aplicativo da Web) com o URI http://localhost:8080/ já cadastrado.
"""
import sys
import json
import getpass
import secrets
import subprocess
import webbrowser
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

REPO = "danielsilvarodriguesdrs-ship-it/bom-dia-daniel"
ESCOPOS = "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/gmail.readonly"
PORTA = 8080
REDIRECT = f"http://localhost:{PORTA}/"  # igual ao URI cadastrado no cliente
SECRET_POR_CONTA = {"pessoal": "GOOGLE_REFRESH_TOKEN_PESSOAL", "campofort": "GOOGLE_REFRESH_TOKEN_CAMPOFORT"}


def gh_secret(nome, valor):
    subprocess.run(["gh", "secret", "set", nome, "--repo", REPO], input=valor.encode(), check=True)
    print(f"  ✔ secret {nome} gravado no GitHub")


def main():
    conta = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    if conta not in SECRET_POR_CONTA:
        sys.exit("Informe a conta: python tools/renovar_google.py pessoal   (ou campofort)")

    print(f"\n== Renovar Google — conta {conta.upper()} ==\n")
    cid = input("Client ID do Google: ").strip()
    csec = getpass.getpass("Client Secret do Google (não aparece ao digitar): ").strip()

    estado = secrets.token_urlsafe(16)
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": REDIRECT, "response_type": "code",
        "scope": ESCOPOS, "access_type": "offline", "prompt": "consent", "state": estado,
    })

    recebido = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            recebido.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>Pronto! Pode fechar esta aba e voltar ao terminal.</h2>".encode())

        def log_message(self, *a):
            pass

    print(f"\nAbrindo o navegador. ENTRE NA CONTA GOOGLE {conta.upper()} e autorize.")
    print("Se aparecer 'O Google não verificou este app', clique em Avançado → Acessar (é o seu próprio app).\n")
    webbrowser.open(url)
    srv = HTTPServer(("localhost", PORTA), Handler)
    while "code" not in recebido and "error" not in recebido:
        srv.handle_request()

    if "error" in recebido:
        sys.exit(f"Autorização recusada: {recebido['error']}")
    if recebido.get("state") != estado:
        sys.exit("Resposta inesperada do Google (state não confere). Tente de novo.")

    dados = urllib.parse.urlencode({
        "code": recebido["code"], "client_id": cid, "client_secret": csec,
        "redirect_uri": REDIRECT, "grant_type": "authorization_code",
    }).encode()
    try:
        with urllib.request.urlopen("https://oauth2.googleapis.com/token", data=dados, timeout=20) as r:
            tok = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Google recusou a troca do código: {e.read().decode()[:200]}")

    if "refresh_token" not in tok:
        sys.exit("O Google não devolveu refresh_token. Remova o acesso em myaccount.google.com/permissions e rode de novo.")

    print("\nGravando no GitHub…")
    gh_secret(SECRET_POR_CONTA[conta], tok["refresh_token"])
    if input("Gravar também este Client ID/Secret no GitHub? (s/N): ").strip().lower() == "s":
        gh_secret("GOOGLE_CLIENT_ID", cid)
        gh_secret("GOOGLE_CLIENT_SECRET", csec)
    print(f"\n✅ Conta {conta} renovada.\n")


if __name__ == "__main__":
    main()
