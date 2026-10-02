"""Formatação de moeda e datas."""

from datetime import datetime

FORMATO_TELA = "%d-%m-%Y"
FORMATO_ARQUIVO = "%Y-%m-%d"  # ordem alfabética == ordem cronológica


def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def data_valida(texto):
    try:
        datetime.strptime(texto, FORMATO_TELA)
        return True
    except ValueError:
        return False


def data_para_arquivo(texto):
    """DD-MM-AAAA -> AAAA-MM-DD."""
    return datetime.strptime(texto, FORMATO_TELA).strftime(FORMATO_ARQUIVO)


def data_para_tela(texto):
    """AAAA-MM-DD -> DD-MM-AAAA."""
    return datetime.strptime(texto, FORMATO_ARQUIVO).strftime(FORMATO_TELA)
