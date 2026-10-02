"""Mostra o conteúdo BRUTO dos arquivos .dat, na ordem física do disco.

Os .dat são binários: abertos num editor de texto parecem "chinês". Aqui a
leitura é sequencial (sem a árvore) e inclui registros excluídos (ativo = 0).
"""

import os


def hexdump(dados):
    linhas = []
    for i in range(0, len(dados), 16):
        bloco = dados[i:i + 16]
        hexa = " ".join(f"{b:02X}" for b in bloco)
        texto = "".join(chr(b) if 32 <= b < 127 else "." for b in bloco)
        linhas.append(f"    {i:04d}  {hexa:<48}  {texto}")
    return "\n".join(linhas)


def relatorio(repo, titulo):
    tam = repo.tamanho_registro
    total = repo.total_registros()
    linhas = [
        "=" * 78,
        f" ARQUIVO: {repo.caminho}   ({titulo})",
        f" Formato struct: '{repo.formato}'  ->  {tam} bytes por registro",
        f" Tamanho: {os.path.getsize(repo.caminho)} bytes = {total} registros x {tam} bytes",
        "=" * 78,
    ]
    primeiro = b""
    with open(repo.caminho, "rb") as f:
        for pos in range(total):
            dados = f.read(tam)
            primeiro = primeiro or dados
            reg = repo.desempacotar(dados)
            situacao = "ATIVO" if reg["ativo"] == 1 else "EXCLUÍDO (ativo=0)"
            campos = ", ".join(f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}"
                               for k, v in reg.items() if k != "ativo")
            linhas.append(f"pos {pos:<3} byte {pos * tam:<5} {situacao:<19} {campos}")
    if primeiro:
        linhas += ["", "Bytes crus do registro 0 (o que o editor de texto 'vê'):", hexdump(primeiro)]
    return "\n".join(linhas) + "\n"


def exportar_txt(financas):
    """Grava cópias legíveis em <pasta>/legivel/<tabela>.txt. Devolve os caminhos."""
    pasta = os.path.join(financas.pasta, "legivel")
    os.makedirs(pasta, exist_ok=True)
    caminhos = []
    for nome, repo in financas.repos.items():
        destino = os.path.join(pasta, f"{nome}.txt")
        with open(destino, "w", encoding="utf-8-sig") as f:
            f.write(relatorio(repo, nome))
        caminhos.append(destino)
    return caminhos
