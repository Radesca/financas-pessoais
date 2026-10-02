"""Ponto de entrada.

    python main.py          # abre o frontend web no navegador (http://127.0.0.1:8000)
    python main.py --cli    # interface de terminal
"""

import os
import sys

from financas import cli, web

# A pasta dados/ fica sempre ao lado deste arquivo, de onde quer que se execute.
PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")

if __name__ == "__main__":
    (cli if "--cli" in sys.argv else web).executar(PASTA_DADOS)
