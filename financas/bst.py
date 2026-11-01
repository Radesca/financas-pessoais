"""Árvore binária de busca (BST) usada como área de índices.

Cada nó guarda a chave primária do registro (``chave``) e a posição dele no
arquivo de dados (``posicao``, a partir de 0). A árvore vive em memória: ao
iniciar, o repositório lê o arquivo de dados do começo ao fim e indexa cada
registro ativo (ver ``Repositorio._carregar_indice``).

Busca, inclusão e exclusão passam primeiro pela árvore; só depois o programa
vai ao arquivo ler ou gravar o registro completo.

Todas as operações são iterativas. Como os códigos são sequenciais, a árvore
fica degenerada (vira uma lista encadeada) e uma versão recursiva estouraria
o limite de recursão do Python com poucos milhares de registros.
A árvore não é balanceada (não é AVL): o custo de cada operação é O(altura).
"""


class No:
    def __init__(self, chave, posicao):
        self.chave = chave
        self.posicao = posicao
        self.esquerda = None
        self.direita = None


class ArvoreBinaria:
    """Para todo nó, as chaves à esquerda são menores e as da direita, maiores."""

    def __init__(self):
        self.raiz = None

    def inserir(self, chave, posicao):
        """Insere a chave; se ela já existir, só atualiza a posição."""
        pai, atual = None, self.raiz
        while atual is not None:
            if chave == atual.chave:
                atual.posicao = posicao
                return
            pai = atual
            atual = atual.esquerda if chave < atual.chave else atual.direita

        novo = No(chave, posicao)
        if pai is None:
            self.raiz = novo
        elif chave < pai.chave:
            pai.esquerda = novo
        else:
            pai.direita = novo

    def buscar(self, chave):
        """Devolve o nó da chave, ou None se ela não existir."""
        atual = self.raiz
        while atual is not None and atual.chave != chave:
            atual = atual.esquerda if chave < atual.chave else atual.direita
        return atual

    def excluir(self, chave):
        """Remove a chave (sem filhos, um filho ou dois filhos)."""
        pai, no = None, self.raiz
        while no is not None and no.chave != chave:
            pai = no
            no = no.esquerda if chave < no.chave else no.direita
        if no is None:
            return

        if no.esquerda is not None and no.direita is not None:
            # Dois filhos: o nó recebe os dados do sucessor (o menor da subárvore
            # direita), e é o sucessor, que tem no máximo um filho, que sai.
            pai, sucessor = no, no.direita
            while sucessor.esquerda is not None:
                pai, sucessor = sucessor, sucessor.esquerda
            no.chave, no.posicao = sucessor.chave, sucessor.posicao
            no = sucessor

        filho = no.esquerda if no.esquerda is not None else no.direita
        if pai is None:
            self.raiz = filho
        elif pai.esquerda is no:
            pai.esquerda = filho
        else:
            pai.direita = filho

    def maior_chave(self):
        """Maior chave da árvore, ou None se ela estiver vazia."""
        atual = self.raiz
        while atual is not None and atual.direita is not None:
            atual = atual.direita
        return None if atual is None else atual.chave

    def em_ordem(self):
        """Lista [(chave, posicao), ...] em ordem crescente de chave."""
        resultado, pilha, atual = [], [], self.raiz
        while pilha or atual is not None:
            while atual is not None:
                pilha.append(atual)
                atual = atual.esquerda
            atual = pilha.pop()
            resultado.append((atual.chave, atual.posicao))
            atual = atual.direita
        return resultado

    def altura(self):
        """Altura da árvore (-1 se vazia). Usada para fins didáticos."""
        maior, pilha = -1, [(self.raiz, 0)] if self.raiz else []
        while pilha:
            no, nivel = pilha.pop()
            maior = max(maior, nivel)
            for filho in (no.esquerda, no.direita):
                if filho is not None:
                    pilha.append((filho, nivel + 1))
        return maior
