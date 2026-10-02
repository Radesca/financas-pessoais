"""Interface de terminal (menus)."""

from . import visualizador
from .servico import CAMPO_TEXTO, ErroNegocio, Financas
from .utils import data_para_arquivo, data_para_tela, data_valida, formatar_moeda

LARGURA = 60


# ------------------------------------------------------------------ entrada
def cabecalho(titulo):
    print(f"\n\n{'=' * LARGURA}\n{titulo.center(LARGURA)}\n{'=' * LARGURA}")


def pausar():
    input("\nPressione ENTER para continuar...")


def ler_numero(mensagem, tipo=int, obrigatorio=True):
    while True:
        texto = input(mensagem).strip().replace(",", ".")
        if not texto and not obrigatorio:
            return None
        try:
            return tipo(texto)
        except ValueError:
            print("Valor inválido.")


def ler_data(mensagem):
    while True:
        texto = input(mensagem).strip()
        if data_valida(texto):
            return data_para_arquivo(texto)
        print("Data inválida. Use DD-MM-AAAA (ex: 24-08-2026).")


def escolher(titulo, itens):
    """Mostra 'codigo - texto' e lê um código."""
    print(f"\n{titulo}:")
    for codigo, texto in itens:
        print(f"  {codigo} - {texto}")
    return ler_numero("Código: ")


def menu(titulo, opcoes, saida="Voltar"):
    """Loop de menu. `opcoes` = {"1": ("Rótulo", funcao)}; "0" sai."""
    while True:
        cabecalho(titulo)
        for tecla, (rotulo, _) in opcoes.items():
            print(f"{tecla} - {rotulo}")
        print(f"0 - {saida}")
        tecla = input("\nOpção: ").strip()
        if tecla == "0":
            return
        if tecla not in opcoes:
            print("Opção inválida.")
            pausar()
            continue
        try:
            opcoes[tecla][1]()
        except ErroNegocio as erro:
            print(f"\n{erro}")
        pausar()


# ---------------------------------------------------------------- telas
class Terminal:
    def __init__(self, financas):
        self.f = financas

    # cadastros simples (pessoas, bancos, categorias)
    def menu_simples(self, tabela, titulo):
        repo, campo = self.f.repos[tabela], CAMPO_TEXTO[tabela]

        def incluir():
            sugestao = repo.proximo_codigo()
            codigo = ler_numero(f"Código (ENTER = {sugestao}): ", obrigatorio=False)
            codigo = self.f.criar_simples(tabela, input(f"{campo.capitalize()}: "), codigo)
            print(f"\nIncluído com o código {codigo}.")

        def listar():
            registros = repo.listar()
            print(f"{'Código':<10}{campo.capitalize()}\n{'-' * 50}")
            for r in registros:
                print(f"{r['codigo']:<10}{r[campo]}")
            if not registros:
                print("Nenhum registro cadastrado.")

        def buscar():
            r = repo.buscar(ler_numero("Código: "))
            print(f"\nCódigo: {r['codigo']}\n{campo.capitalize()}: {r[campo]}" if r else "\nNão encontrado.")

        def excluir():
            print("\nExcluído." if repo.excluir(ler_numero("Código: ")) else "\nNão encontrado.")

        menu(f"CADASTRO - {titulo}", {"1": ("Incluir", incluir), "2": ("Listar", listar),
                                       "3": ("Buscar por código", buscar), "4": ("Excluir", excluir)})

    # contas
    def _linha_conta(self, c):
        return (f"{c['codigo']:<6}{c['descricao']:<22}{c['banco']:<18}"
                f"{c['titular']:<18}{formatar_moeda(c['saldo']):>12}")

    def _tabela_contas(self):
        contas = self.f.contas_detalhadas()
        if not contas:
            print("Nenhuma conta cadastrada.")
            return
        print(f"{'Cód':<6}{'Descrição':<22}{'Banco':<18}{'Titular':<18}{'Saldo':>12}\n{'-' * 76}")
        for c in contas:
            print(self._linha_conta(c))
        print("-" * 76)
        print(f"SALDO GERAL: {formatar_moeda(self.f.saldo_geral())}")

    def menu_contas(self):
        def incluir():
            if not (self.f.bancos.listar() and self.f.pessoas.listar()):
                raise ErroNegocio("Cadastre ao menos um Banco e uma Pessoa antes.")
            sugestao = self.f.contas.proximo_codigo()
            codigo = ler_numero(f"Código da conta (ENTER = {sugestao}): ", obrigatorio=False)
            cod_banco = escolher("Bancos", [(b["codigo"], b["descricao"]) for b in self.f.bancos.listar()])
            cod_pessoa = escolher("Pessoas", [(p["codigo"], p["nome"]) for p in self.f.pessoas.listar()])
            descricao = input("Descrição (ex: Conta Corrente): ")
            saldo = ler_numero("Saldo inicial: ", float)
            self.f.criar_conta(cod_banco, cod_pessoa, descricao, saldo, codigo)
            print("\nConta incluída.")

        def buscar():
            c = self.f.contas.buscar(ler_numero("Código da conta: "))
            if c is None:
                print("\nConta não encontrada.")
                return
            c = self.f.descrever_conta(c)
            print(f"\nCódigo: {c['codigo']}\nDescrição: {c['descricao']}\nBanco: {c['banco']}\n"
                  f"Titular: {c['titular']}\nSaldo: {formatar_moeda(c['saldo'])}")

        def excluir():
            print("\nExcluída." if self.f.contas.excluir(ler_numero("Código da conta: ")) else "\nNão encontrada.")

        menu("CADASTRO - Contas Bancárias", {"1": ("Incluir", incluir), "2": ("Listar", self._tabela_contas),
                                              "3": ("Buscar por código", buscar), "4": ("Excluir", excluir)})

    # transações
    def lancar(self):
        f = self.f
        if not (f.categorias.listar() and f.contas.listar()):
            raise ErroNegocio("Cadastre ao menos uma Categoria e uma Conta antes.")
        cod_cat = escolher("Categorias", [(c["codigo"], c["descricao"]) for c in f.categorias.listar()])
        cod_conta = escolher("Contas", [(c["codigo"], f"{c['descricao']} ({c['banco']})")
                                        for c in f.contas_detalhadas()])
        data = ler_data("Data (DD-MM-AAAA): ")
        valor = ler_numero("Valor: ", float)
        tipo = ""
        while tipo not in ("D", "C"):
            tipo = input("Tipo (D = Débito / C = Crédito): ").strip().upper()
        codigo, saldo = f.lancar_transacao(cod_cat, cod_conta, data, valor, tipo)
        print(f"\nTransação nº {codigo} lançada. Novo saldo da conta: {formatar_moeda(saldo)}")

    def listar_periodo(self):
        ini = ler_data("Data inicial (DD-MM-AAAA): ")
        fim = ler_data("Data final (DD-MM-AAAA): ")
        lista = sorted(self.f.transacoes_por_periodo(ini, fim), key=lambda t: t["data"])
        if not lista:
            print("\nNenhuma transação no período.")
            return
        print(f"\n{'Nº':<6}{'Data':<12}{'Categoria':<18}{'Conta':<16}{'Tipo':<6}{'Valor':>12}\n{'-' * 72}")
        for t in lista:
            print(f"{t['codigo']:<6}{data_para_tela(t['data']):<12}{t['categoria']:<18}"
                  f"{t['conta']:<16}{t['tipo']:<6}{formatar_moeda(t['valor']):>12}")
        print("-" * 72)
        print(f"Saldo das transações no período: {formatar_moeda(self.f.saldo_das_transacoes(lista))}")

    def excluir_transacao(self):
        ok = self.f.excluir_transacao(ler_numero("Número da transação: "))
        print("\nExcluída e saldo estornado." if ok else "\nTransação não encontrada.")

    def principal(self):
        def ver_dados():
            for caminho in visualizador.exportar_txt(self.f):
                print("Gerado:", caminho)

        menu("SISTEMA DE GESTÃO DE FINANÇAS PESSOAIS", {
            "1": ("Pessoas", lambda: self.menu_simples("pessoas", "Pessoas")),
            "2": ("Bancos", lambda: self.menu_simples("bancos", "Bancos")),
            "3": ("Categorias de Gastos", lambda: self.menu_simples("categorias", "Categorias")),
            "4": ("Contas Bancárias", self.menu_contas),
            "5": ("Lançar transação", self.lancar),
            "6": ("Transações por período", self.listar_periodo),
            "7": ("Excluir transação", self.excluir_transacao),
            "8": ("Saldos de todas as contas", self._tabela_contas),
            "9": ("Gerar cópias legíveis dos .dat", ver_dados),
        }, saida="Sair")


def executar(pasta="dados"):
    Terminal(Financas(pasta)).principal()
