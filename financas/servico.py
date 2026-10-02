"""Regras de negócio, compartilhadas pela interface de terminal e pela web.

Datas entram e saem em AAAA-MM-DD (formato do arquivo).
"""

import os

from .repositorio import Repositorio

# Esquema de cada tabela: (nome do campo, formato struct). "Ns" = texto de N bytes.
ESQUEMAS = {
    "pessoas": [("codigo", "i"), ("nome", "30s")],
    "bancos": [("codigo", "i"), ("descricao", "40s")],
    "categorias": [("codigo", "i"), ("descricao", "40s")],
    "contas": [("codigo", "i"), ("cod_banco", "i"), ("cod_pessoa", "i"),
               ("descricao", "30s"), ("saldo", "d")],
    "transacoes": [("codigo", "i"), ("cod_cat", "i"), ("cod_conta", "i"),
                   ("data", "10s"), ("valor", "d"), ("tipo", "1s")],
}
# Tabelas que são só "código + texto" e o nome desse campo de texto.
CAMPO_TEXTO = {"pessoas": "nome", "bancos": "descricao", "categorias": "descricao"}


class ErroNegocio(ValueError):
    """Violação de regra de negócio (mensagem pronta para o usuário)."""


def efeito_no_saldo(tipo, valor):
    return valor if tipo == "C" else -valor


class Financas:
    def __init__(self, pasta="dados"):
        self.pasta = pasta
        self.pessoas = Repositorio(os.path.join(pasta, "pessoas.dat"), ESQUEMAS["pessoas"])
        self.bancos = Repositorio(os.path.join(pasta, "bancos.dat"), ESQUEMAS["bancos"])
        self.categorias = Repositorio(os.path.join(pasta, "categorias.dat"), ESQUEMAS["categorias"])
        self.contas = Repositorio(os.path.join(pasta, "contas.dat"), ESQUEMAS["contas"])
        self.transacoes = Repositorio(os.path.join(pasta, "transacoes.dat"), ESQUEMAS["transacoes"])
        self.repos = {nome: getattr(self, nome) for nome in ESQUEMAS}

    def _descricao(self, tabela, codigo, padrao):
        registro = self.repos[tabela].buscar(codigo)
        if registro is None:
            return padrao
        return registro[CAMPO_TEXTO.get(tabela, "descricao")]

    # ------------------------------------------------------------ cadastros
    def criar_simples(self, tabela, texto, codigo=None):
        texto = (texto or "").strip()
        if not texto:
            raise ErroNegocio("O texto não pode ser vazio.")
        repo = self.repos[tabela]
        codigo = codigo or repo.proximo_codigo()
        if repo.existe(codigo):
            raise ErroNegocio(f"Já existe um registro com o código {codigo}.")
        repo.inserir({"codigo": codigo, CAMPO_TEXTO[tabela]: texto})
        return codigo

    def criar_conta(self, cod_banco, cod_pessoa, descricao, saldo, codigo=None):
        if not self.bancos.existe(cod_banco):
            raise ErroNegocio("Banco inválido.")
        if not self.pessoas.existe(cod_pessoa):
            raise ErroNegocio("Pessoa inválida.")
        codigo = codigo or self.contas.proximo_codigo()
        if self.contas.existe(codigo):
            raise ErroNegocio(f"Já existe uma conta com o código {codigo}.")
        self.contas.inserir({"codigo": codigo, "cod_banco": cod_banco, "cod_pessoa": cod_pessoa,
                             "descricao": (descricao or "").strip(), "saldo": saldo})
        return codigo

    def excluir(self, tabela, codigo):
        if tabela == "transacoes":
            return self.excluir_transacao(codigo)
        return self.repos[tabela].excluir(codigo)

    # ----------------------------------------------------------- transações
    def _ajustar_saldo(self, cod_conta, delta):
        conta = self.contas.buscar(cod_conta)
        if conta is None:
            return None
        conta["saldo"] += delta
        self.contas.atualizar(conta)
        return conta["saldo"]

    def lancar_transacao(self, cod_cat, cod_conta, data, valor, tipo):
        """Grava a transação e ajusta o saldo da conta. Devolve (codigo, novo_saldo)."""
        if not self.categorias.existe(cod_cat):
            raise ErroNegocio("Categoria inválida.")
        if not self.contas.existe(cod_conta):
            raise ErroNegocio("Conta inválida.")
        if tipo not in ("D", "C"):
            raise ErroNegocio("Tipo deve ser D (débito) ou C (crédito).")
        if valor <= 0:
            raise ErroNegocio("O valor deve ser maior que zero.")
        codigo = self.transacoes.proximo_codigo()
        self.transacoes.inserir({"codigo": codigo, "cod_cat": cod_cat, "cod_conta": cod_conta,
                                 "data": data, "valor": valor, "tipo": tipo})
        return codigo, self._ajustar_saldo(cod_conta, efeito_no_saldo(tipo, valor))

    def excluir_transacao(self, codigo):
        """Exclui e estorna o efeito no saldo (se a conta ainda existir)."""
        t = self.transacoes.buscar(codigo)
        if t is None:
            return False
        self._ajustar_saldo(t["cod_conta"], -efeito_no_saldo(t["tipo"], t["valor"]))
        return self.transacoes.excluir(codigo)

    def transacoes_por_periodo(self, data_ini, data_fim):
        return [self.descrever_transacao(t) for t in self.transacoes.listar()
                if data_ini <= t["data"] <= data_fim]

    # -------------------------------------------------- visões enriquecidas
    def descrever_transacao(self, t):
        return {**t,
                "categoria": self._descricao("categorias", t["cod_cat"], "(categoria excluída)"),
                "conta": self._descricao("contas", t["cod_conta"], "(conta excluída)")}

    def descrever_conta(self, c):
        return {**c,
                "banco": self._descricao("bancos", c["cod_banco"], "(banco excluído)"),
                "titular": self._descricao("pessoas", c["cod_pessoa"], "(pessoa excluída)")}

    def contas_detalhadas(self):
        return [self.descrever_conta(c) for c in self.contas.listar()]

    def saldo_geral(self):
        return sum(c["saldo"] for c in self.contas.listar())

    @staticmethod
    def saldo_das_transacoes(lista):
        return sum(efeito_no_saldo(t["tipo"], t["valor"]) for t in lista)
