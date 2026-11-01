"""Arquivo indexado genérico.

- Área de dados: arquivo binário de registros de tamanho fixo (struct).
- Área de índices: BST em memória, chave (codigo) -> posição no arquivo.
- Exclusão lógica: o registro permanece no arquivo com ``ativo = 0``.

Cada tabela é descrita só por uma lista de campos ``(nome, formato_struct)``;
o campo ``ativo`` é acrescentado automaticamente no fim.
"""

import os
import struct

from .bst import ArvoreBinaria

CAMPO_CODIGO = "codigo"
CAMPO_ATIVO = "ativo"


class Repositorio:
    def __init__(self, caminho, campos):
        self.caminho = caminho
        self.campos = [*campos, (CAMPO_ATIVO, "i")]
        self.formato = "<" + "".join(fmt for _, fmt in self.campos)
        self.tamanho_registro = struct.calcsize(self.formato)

        os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
        if not os.path.exists(caminho):
            open(caminho, "wb").close()
        self.indice = self._carregar_indice()

    # ---------------------------------------------------------------- bytes
    def empacotar(self, registro):
        valores = [
            str(registro[nome]).encode("utf-8") if fmt.endswith("s") else registro[nome]
            for nome, fmt in self.campos
        ]
        return struct.pack(self.formato, *valores)

    def desempacotar(self, dados):
        valores = struct.unpack(self.formato, dados)
        return {
            nome: v.split(b"\x00", 1)[0].decode("utf-8", errors="ignore") if isinstance(v, bytes) else v
            for (nome, _), v in zip(self.campos, valores)
        }

    # ------------------------------------------------------- área de dados
    def total_registros(self):
        return os.path.getsize(self.caminho) // self.tamanho_registro

    def _ler(self, posicao, arquivo=None):
        if arquivo is None:
            with open(self.caminho, "rb") as f:
                return self._ler(posicao, f)
        arquivo.seek(posicao * self.tamanho_registro)
        return self.desempacotar(arquivo.read(self.tamanho_registro))

    def _escrever(self, posicao, registro):
        with open(self.caminho, "r+b") as f:
            f.seek(posicao * self.tamanho_registro)
            f.write(self.empacotar(registro))

    def _carregar_indice(self):
        """Lê o arquivo sequencialmente e indexa os registros ativos."""
        indice = ArvoreBinaria()
        with open(self.caminho, "rb") as f:
            for pos in range(self.total_registros()):
                registro = self.desempacotar(f.read(self.tamanho_registro))
                if registro[CAMPO_ATIVO] == 1:
                    indice.inserir(registro[CAMPO_CODIGO], pos)
        return indice

    # ---------------------------------------------------------------- CRUD
    def existe(self, codigo):
        return self.indice.buscar(codigo) is not None

    def inserir(self, registro):
        codigo = registro[CAMPO_CODIGO]
        if self.existe(codigo):
            raise ValueError(f"Já existe um registro com código {codigo}.")
        registro[CAMPO_ATIVO] = 1
        posicao = self.total_registros()
        self._escrever(posicao, registro)
        self.indice.inserir(codigo, posicao)

    def buscar(self, codigo):
        no = self.indice.buscar(codigo)
        return None if no is None else self._ler(no.posicao)

    def atualizar(self, registro):
        no = self.indice.buscar(registro[CAMPO_CODIGO])
        if no is None:
            raise ValueError("Registro não encontrado.")
        registro[CAMPO_ATIVO] = 1
        self._escrever(no.posicao, registro)

    def excluir(self, codigo):
        no = self.indice.buscar(codigo)
        if no is None:
            return False
        registro = self._ler(no.posicao)
        registro[CAMPO_ATIVO] = 0
        self._escrever(no.posicao, registro)
        self.indice.excluir(codigo)
        return True

    def listar(self):
        """Registros ativos em ordem crescente de código (percurso em-ordem)."""
        with open(self.caminho, "rb") as f:
            return [self._ler(pos, f) for _, pos in self.indice.em_ordem()]

    def proximo_codigo(self):
        maior = self.indice.maior_chave()
        return 1 if maior is None else maior + 1
