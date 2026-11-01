import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from financas.servico import ErroNegocio, Financas


class TestFinancas(unittest.TestCase):
    def setUp(self):
        self._pasta = tempfile.TemporaryDirectory()
        self.pasta = self._pasta.name
        self.f = Financas(self.pasta)
        self.pessoa = self.f.criar_simples("pessoas", "Ana")
        self.banco = self.f.criar_simples("bancos", "Nubank")
        self.categoria = self.f.criar_simples("categorias", "Mercado")
        self.conta = self.f.criar_conta(self.banco, self.pessoa, "Corrente", 1000.0)

    def tearDown(self):
        self._pasta.cleanup()

    def lancar(self, valor, tipo, data="2026-10-05"):
        return self.f.lancar_transacao(self.categoria, self.conta, data, valor, tipo)

    def saldo(self):
        return self.f.contas.buscar(self.conta)["saldo"]

    def test_debito_e_credito_ajustam_o_saldo(self):
        self.lancar(250.0, "D")
        self.assertEqual(self.saldo(), 750.0)
        self.lancar(100.0, "C")
        self.assertEqual(self.saldo(), 850.0)
        self.assertEqual(self.f.saldo_geral(), 850.0)

    def test_excluir_transacao_estorna_o_saldo(self):
        codigo, _ = self.lancar(250.0, "D")
        self.assertTrue(self.f.excluir_transacao(codigo))
        self.assertEqual(self.saldo(), 1000.0)
        self.assertFalse(self.f.excluir_transacao(codigo))

    def test_codigos_sao_sequenciais(self):
        self.assertEqual(self.lancar(1.0, "D")[0], 1)
        self.assertEqual(self.lancar(1.0, "D")[0], 2)

    def test_dados_continuam_depois_de_reabrir(self):
        codigo, _ = self.lancar(10.0, "D")
        apagada, _ = self.lancar(20.0, "D")
        self.f.excluir_transacao(apagada)
        reaberto = Financas(self.pasta)
        self.assertIsNotNone(reaberto.transacoes.buscar(codigo))
        self.assertIsNone(reaberto.transacoes.buscar(apagada))
        self.assertEqual(reaberto.contas.buscar(self.conta)["saldo"], 990.0)

    def test_validacoes(self):
        casos = [
            lambda: self.f.lancar_transacao(99, self.conta, "2026-10-05", 10.0, "D"),
            lambda: self.f.lancar_transacao(self.categoria, 99, "2026-10-05", 10.0, "D"),
            lambda: self.lancar(10.0, "X"),
            lambda: self.lancar(0.0, "D"),
            lambda: self.lancar(-5.0, "D"),
            lambda: self.lancar(float("nan"), "D"),
            lambda: self.lancar(float("inf"), "C"),
            lambda: self.lancar(10.0, "D", data="05/10/2026"),
            lambda: self.f.criar_simples("pessoas", "   "),
            lambda: self.f.criar_simples("pessoas", "A" * 31),
            lambda: self.f.criar_conta(99, self.pessoa, "x", 1.0),
            lambda: self.f.criar_conta(self.banco, self.pessoa, "x", float("nan")),
        ]
        for i, caso in enumerate(casos):
            with self.subTest(caso=i), self.assertRaises(ErroNegocio):
                caso()
        self.assertEqual(self.saldo(), 1000.0)

    def test_acentos_contam_em_bytes(self):
        self.f.criar_simples("pessoas", "ã" * 15)  # 30 bytes: cabe
        with self.assertRaises(ErroNegocio):
            self.f.criar_simples("pessoas", "ã" * 16)  # 32 bytes: não cabe

    def test_listar_milhares_de_transacoes(self):
        for _ in range(1500):
            self.lancar(1.0, "C")
        self.assertEqual(len(self.f.transacoes.listar()), 1500)
        self.assertEqual(len(Financas(self.pasta).transacoes.listar()), 1500)


if __name__ == "__main__":
    unittest.main()
