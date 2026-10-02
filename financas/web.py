"""Frontend web: servidor HTTP (só biblioteca padrão) + página em static/index.html.

API:
    GET    /api/dados             -> todas as tabelas + totais
    POST   /api/<tabela>          -> cria registro (corpo JSON)
    DELETE /api/<tabela>/<codigo> -> exclui registro
"""

import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from .servico import CAMPO_TEXTO, ErroNegocio, Financas

PAGINA = os.path.join(os.path.dirname(__file__), "static", "index.html")


def _criar(f, tabela, d):
    """Despacha o POST para a regra de negócio da tabela."""
    if tabela in CAMPO_TEXTO:
        return f.criar_simples(tabela, d.get("texto"))
    if tabela == "contas":
        return f.criar_conta(int(d["cod_banco"]), int(d["cod_pessoa"]),
                             d.get("descricao"), float(d["saldo"]))
    if tabela == "transacoes":
        codigo, _ = f.lancar_transacao(int(d["cod_cat"]), int(d["cod_conta"]), d["data"],
                                       float(d["valor"]), d["tipo"])
        return codigo
    raise ErroNegocio("Tabela desconhecida.")


def _dados(f):
    transacoes = [f.descrever_transacao(t) for t in f.transacoes.listar()]
    return {
        "pessoas": f.pessoas.listar(),
        "bancos": f.bancos.listar(),
        "categorias": f.categorias.listar(),
        "contas": f.contas_detalhadas(),
        "transacoes": transacoes,
        "saldo_geral": f.saldo_geral(),
    }


def criar_handler(financas):
    class Handler(BaseHTTPRequestHandler):
        def _responder(self, status, corpo, tipo="application/json"):
            if not isinstance(corpo, bytes):
                corpo = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", f"{tipo}; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def _tratar(self, acao):
            try:
                self._responder(200, acao())
            except (ErroNegocio, KeyError, IndexError, ValueError, TypeError) as erro:  # JSONDecodeError é ValueError
                mensagem = str(erro) if isinstance(erro, ErroNegocio) else "Dados inválidos."
                self._responder(400, {"erro": mensagem})

        def do_GET(self):
            if self.path == "/api/dados":
                return self._responder(200, _dados(financas))
            if self.path in ("/", "/index.html"):
                with open(PAGINA, "rb") as f:
                    return self._responder(200, f.read(), "text/html")
            self._responder(404, {"erro": "Não encontrado."})

        def do_POST(self):
            tabela = self.path.removeprefix("/api/")
            tamanho = int(self.headers.get("Content-Length", 0))
            self._tratar(lambda: {"codigo": _criar(financas, tabela, json.loads(self.rfile.read(tamanho)))})

        def do_DELETE(self):
            partes = self.path.removeprefix("/api/").split("/")
            self._tratar(lambda: {"excluido": partes[0] in financas.repos
                                  and financas.excluir(partes[0], int(partes[1]))})

        def log_message(self, *_):  # silencia o log por requisição
            pass

    return Handler


def executar(pasta="dados", porta=8000):
    servidor = HTTPServer(("127.0.0.1", porta), criar_handler(Financas(pasta)))
    url = f"http://127.0.0.1:{porta}"
    print(f"Finanças rodando em {url}  (Ctrl+C para parar)")
    threading.Timer(0.5, webbrowser.open, args=[url]).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")
