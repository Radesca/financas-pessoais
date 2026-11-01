import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from financas.bst import ArvoreBinaria


def montar(chaves):
    arvore = ArvoreBinaria()
    for posicao, chave in enumerate(chaves):
        arvore.inserir(chave, posicao)
    return arvore


class TestArvoreBinaria(unittest.TestCase):
    def test_busca_devolve_a_posicao(self):
        arvore = montar([50, 30, 70, 20, 40])
        self.assertEqual(arvore.buscar(40).posicao, 4)
        self.assertIsNone(arvore.buscar(99))

    def test_em_ordem_fica_crescente(self):
        arvore = montar([50, 30, 70, 20, 40, 60, 80])
        self.assertEqual([c for c, _ in arvore.em_ordem()], [20, 30, 40, 50, 60, 70, 80])

    def test_chave_repetida_so_atualiza_a_posicao(self):
        arvore = montar([10, 5])
        arvore.inserir(5, 99)
        self.assertEqual(arvore.buscar(5).posicao, 99)
        self.assertEqual(len(arvore.em_ordem()), 2)

    def test_maior_chave(self):
        self.assertIsNone(ArvoreBinaria().maior_chave())
        self.assertEqual(montar([50, 30, 70, 60]).maior_chave(), 70)

    def test_exclusao_sem_filhos(self):
        arvore = montar([50, 30, 70])
        arvore.excluir(30)
        self.assertEqual([c for c, _ in arvore.em_ordem()], [50, 70])

    def test_exclusao_com_um_filho(self):
        arvore = montar([50, 30, 20])
        arvore.excluir(30)
        self.assertEqual([c for c, _ in arvore.em_ordem()], [20, 50])

    def test_exclusao_com_dois_filhos(self):
        arvore = montar([50, 30, 70, 20, 40, 60, 80])
        arvore.excluir(50)
        self.assertEqual([c for c, _ in arvore.em_ordem()], [20, 30, 40, 60, 70, 80])
        self.assertIsNone(arvore.buscar(50))
        self.assertEqual(arvore.buscar(60).posicao, 5)

    def test_exclusao_da_raiz_e_de_chave_inexistente(self):
        arvore = montar([10])
        arvore.excluir(99)
        arvore.excluir(10)
        self.assertEqual(arvore.em_ordem(), [])
        self.assertEqual(arvore.altura(), -1)

    def test_arvore_degenerada_com_muitos_registros(self):
        """Códigos sequenciais formam uma cadeia; não pode estourar a recursão."""
        total = 5000
        arvore = montar(range(1, total + 1))
        self.assertEqual(arvore.altura(), total - 1)
        self.assertEqual(len(arvore.em_ordem()), total)
        arvore.excluir(2500)
        self.assertIsNone(arvore.buscar(2500))
        self.assertEqual(len(arvore.em_ordem()), total - 1)


if __name__ == "__main__":
    unittest.main()
