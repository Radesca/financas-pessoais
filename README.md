# Finanças Pessoais

Sistema de gestão de finanças pessoais feito para a disciplina **Algoritmo e Estrutura de Dados II** da **FEMA**.

A ideia da disciplina é a de **arquivos indexados**: os dados ficam em arquivos binários de registros de tamanho fixo, e o índice é uma **árvore binária de busca (BST)** mantida em memória. Não há banco de dados.

Sem dependências: só Python 3.9+ e a biblioteca padrão.

**Autor:** Henrique Radesca · [LinkedIn](https://www.linkedin.com/in/henrique-radesca) · [GitHub](https://github.com/Radesca)

## Como usar

```bash
python main.py          # abre o frontend web no navegador (http://127.0.0.1:8000)
python main.py --cli    # interface de terminal
```

Os arquivos `.dat` são criados na pasta `dados/` na primeira execução (a pasta não vai para o Git).

## Funcionalidades

- Cadastro de pessoas, bancos, categorias de gastos e contas bancárias
- Lançamento de transações (débito/crédito) com atualização automática do saldo
- Exclusão de transação com estorno do saldo
- Listagem de transações por período e saldo de todas as contas
- Cópias legíveis dos `.dat` (hexdump + registros excluídos) em `dados/legivel/`

## Arquitetura

| Camada | Arquivo | O que faz |
|---|---|---|
| Frontend | `financas/static/index.html` | Página única em HTML, CSS e JavaScript puros (sem framework), que fala com a API por `fetch` |
| API / back-end | `financas/web.py` | Servidor HTTP com `http.server` e API JSON (`GET /api/dados`, `POST /api/<tabela>`, `DELETE /api/<tabela>/<codigo>`) |
| Terminal | `financas/cli.py` | Menus de terminal, usando as mesmas regras do back-end |
| Regras de negócio | `financas/servico.py` | Validações, saldo das contas, estorno; compartilhadas pela web e pelo terminal |
| Arquivo indexado | `financas/repositorio.py` | CRUD genérico sobre arquivo binário (`struct`) com exclusão lógica |
| Índice | `financas/bst.py` | Árvore binária de busca: `código -> posição no arquivo` |
| Apoio | `financas/utils.py`, `financas/visualizador.py` | Moeda e datas; leitura crua dos `.dat` |

```
navegador / terminal  ->  servico.py (regras)  ->  repositorio.py  ->  bst.py (índice, na RAM)
                                                                   ->  arquivos .dat (disco)
```

## Como funciona

- **Esquema:** cada tabela é só uma lista de campos `(nome, formato struct)` em `servico.py`. O campo `ativo` é acrescentado no fim de todos os registros.
- **Inserção:** o registro é gravado no fim do `.dat` e `(código -> posição)` entra na BST.
- **Busca:** a BST devolve a posição; o registro é lido com `seek(posição x tamanho)`.
- **Exclusão:** lógica. O registro fica no arquivo com `ativo = 0` e o nó sai da BST.
- **Ao iniciar:** o arquivo é lido do começo ao fim e os registros ativos reconstroem a árvore.
- **Transação:** lançar atualiza o saldo da conta; excluir faz o estorno.

## Limitações conhecidas

- **A BST não é balanceada.** Como os códigos são sequenciais (1, 2, 3...), a árvore vira uma cadeia e cada operação custa O(n). Uma AVL ou árvore rubro-negra resolveria. Por isso as operações da árvore são iterativas: a versão recursiva estourava o limite de recursão do Python com ~1.000 registros.
- **Textos têm tamanho máximo** (30 ou 40 bytes, dependendo do campo), porque os registros têm tamanho fixo.
- **Valores em `float`** (`struct` `d`). Para um sistema real, o ideal seria `Decimal` ou centavos inteiros.
- **Sem integridade referencial:** excluir um banco ou pessoa não é bloqueado; as telas mostram "(banco excluído)".
- **Um usuário, sem autenticação**, e o servidor escuta só em `127.0.0.1`.

## Testes

```bash
python -m unittest discover -s tests
```

Cobrem a árvore (inclusão, busca, os três casos de exclusão e uma árvore com 5.000 nós em cadeia) e as regras de negócio (saldo, estorno, persistência, validações).
