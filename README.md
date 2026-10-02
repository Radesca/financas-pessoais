# Finanças Pessoais

Sistema de gestão de finanças pessoais desenvolvido como projeto da disciplina **Estrutura de Dados II** da **FEMA**.
Demonstra **arquivos indexados**: os dados ficam em arquivos binários de registros de tamanho fixo e o
índice é uma **árvore binária de busca (BST)** mantida em memória.

Sem dependências — só Python 3.9+.

## Como usar

```bash
python main.py          # abre o frontend web no navegador (http://127.0.0.1:8000)
python main.py --cli    # interface de terminal
```

Os arquivos `.dat` são criados na pasta `dados/` na primeira execução.

## Funcionalidades

- Cadastro de pessoas, bancos, categorias de gastos e contas bancárias
- Lançamento de transações (débito/crédito) com atualização automática do saldo
- Exclusão de transação com estorno do saldo
- Listagem de transações por período e saldo de todas as contas
- Geração de cópias legíveis dos `.dat` (hexdump + registros excluídos) em `dados/legivel/`

## Estrutura

```
main.py                 ponto de entrada
financas/
  bst.py                árvore binária de busca (índice)
  repositorio.py        arquivo indexado genérico (CRUD, exclusão lógica)
  servico.py            esquemas das tabelas e regras de negócio
  cli.py                interface de terminal
  web.py                servidor HTTP + API JSON
  static/index.html     frontend web
  visualizador.py       leitura crua dos .dat
  utils.py              moeda e datas
```

## Como funciona

- **Inserção:** o registro é gravado no fim do `.dat` e `(código → posição)` entra na BST.
- **Busca:** a BST devolve a posição; o registro é lido com `seek(posição × tamanho)`.
- **Exclusão:** lógica — o registro fica no arquivo com `ativo = 0` e o nó sai da BST.
- **Inicialização:** cada `.dat` é lido sequencialmente para reconstruir a BST.
- **Listagem:** percurso em-ordem da BST (códigos crescentes).

Autor: Henrique dos Santos Radesca
