# -*- coding: utf-8 -*-
"""
bst.py
======
Implementação da Árvore Binária de Busca (BST) usada como ÁREA DE ÍNDICES
do sistema (conforme material "Árvores Binárias" / "Organização Básica de
Arquivos - Arquivos Indexados").

Cada nó guarda:
    - chave    -> o código (chave primária) do registro (ex.: codigo da Pessoa)
    - posicao  -> a posição (número do registro, começando em 0) do registro
                  correspondente dentro do ARQUIVO DE DADOS em disco

A árvore inteira vive em memória (RAM). Quando o programa é iniciado, o
arquivo de dados é lido sequencialmente do início ao fim e cada registro
ativo é inserido na árvore (ver repositorio.py -> _carregar_indice).

Isso reproduz exatamente a ideia da Aula de Arquivos Indexados: a busca,
inclusão e exclusão são sempre feitas primeiro na ÁREA DE ÍNDICES (aqui, a
árvore) e só depois vão até a ÁREA DE DADOS (o arquivo em disco) para
ler/gravar o registro completo.
"""


class No:
    """Um nó da árvore binária. Equivalente ao 'struct No' do material em C++."""

    def __init__(self, chave, posicao):
        self.chave = chave
        self.posicao = posicao
        self.esquerda = None
        self.direita = None


class ArvoreBinaria:
    """Árvore Binária de Busca (BST) simples, sem balanceamento (não é AVL).

    Mantém a propriedade: para qualquer nó, tudo à esquerda é menor e tudo
    à direita é maior que a chave do nó (igual ao slide "Árvores Binárias").
    """

    def __init__(self):
        self.raiz = None

    # ------------------------------------------------------------------
    # INCLUSÃO (versão iterativa, igual ao slide "Árvores Binárias -
    # Inclusão de novo Nó")
    # ------------------------------------------------------------------
    def inserir(self, chave, posicao):
        novo = No(chave, posicao)

        if self.raiz is None:
            self.raiz = novo
            return

        atual = self.raiz
        pai = None
        while atual is not None:
            pai = atual
            if chave < atual.chave:
                atual = atual.esquerda
            elif chave > atual.chave:
                atual = atual.direita
            else:
                # Chave já existe: apenas atualiza a posição no arquivo
                # (acontece, por exemplo, depois de um "update" físico).
                atual.posicao = posicao
                return

        if chave < pai.chave:
            pai.esquerda = novo
        else:
            pai.direita = novo

    # ------------------------------------------------------------------
    # BUSCA (versão iterativa, igual ao slide "Árvores Binárias - Busca
    # de Nó")
    # ------------------------------------------------------------------
    def buscar(self, chave):
        atual = self.raiz
        while atual is not None:
            if chave == atual.chave:
                return atual
            elif chave < atual.chave:
                atual = atual.esquerda
            else:
                atual = atual.direita
        return None

    # ------------------------------------------------------------------
    # EXCLUSÃO (versão recursiva, igual ao slide "Árvores Binárias -
    # Exclusão de Nó": trata os 3 casos -> sem filhos, um filho, dois
    # filhos, usando o "menor da sub-árvore direita" como substituto)
    # ------------------------------------------------------------------
    def excluir(self, chave):
        self.raiz = self._excluir(self.raiz, chave)

    def _excluir(self, raiz, chave):
        if raiz is None:
            return None

        if chave < raiz.chave:
            raiz.esquerda = self._excluir(raiz.esquerda, chave)
        elif chave > raiz.chave:
            raiz.direita = self._excluir(raiz.direita, chave)
        else:
            # Encontrou o nó a ser removido
            if raiz.esquerda is None and raiz.direita is None:
                # Caso 1: não possui nenhum filho
                return None
            elif raiz.esquerda is None:
                # Caso 2: possui apenas o filho direito
                return raiz.direita
            elif raiz.direita is None:
                # Caso 2: possui apenas o filho esquerdo
                return raiz.esquerda
            else:
                # Caso 3: possui dois filhos -> substitui pelo menor
                # elemento da sub-árvore da direita (sucessor em-ordem)
                aux = self._menor(raiz.direita)
                raiz.chave = aux.chave
                raiz.posicao = aux.posicao
                raiz.direita = self._excluir(raiz.direita, aux.chave)
        return raiz

    def _menor(self, no):
        atual = no
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual

    # ------------------------------------------------------------------
    # PERCURSO EM-ORDEM (EMD): usado para listar os registros em ordem
    # crescente de chave, sem precisar reler o arquivo inteiro fora de
    # ordem.
    # ------------------------------------------------------------------
    def em_ordem(self):
        """Retorna uma lista [(chave, posicao), ...] em ordem crescente."""
        resultado = []
        self._em_ordem(self.raiz, resultado)
        return resultado

    def _em_ordem(self, no, resultado):
        if no is not None:
            self._em_ordem(no.esquerda, resultado)
            resultado.append((no.chave, no.posicao))
            self._em_ordem(no.direita, resultado)

    def altura(self):
        """Altura da árvore (nível máximo). Só usada para fins didáticos."""
        return self._altura(self.raiz)

    def _altura(self, no):
        if no is None:
            return -1
        return 1 + max(self._altura(no.esquerda), self._altura(no.direita))
