# ============================================================
# main.py - Orquestrador principal do robô NCM
# ============================================================
from pathlib import Path
import os
import sys
import time
from uuid import uuid4

from acesso_ibroker import baixar_jsp
from executa_jsp    import abrir_ultimo_jsp
from login_ibroker  import executar_login 
from relatorio_erros import enviar_relatorio, montar_payload
from configuracao import USUARIO, SENHA
#from atualiza_ncm   import executar_atualizacao_ncm


DOWNLOAD_DIR = Path(os.environ.get("IBROKER_DOWNLOAD_DIR", str(Path.home() / "Downloads")))

def main():
    """Mantém download → abertura → login; reporta falhas ao n8n."""
    inicio = time.monotonic()
    execucao_id = str(uuid4())
    etapa = "download"

    def registrar_etapa(valor):
        nonlocal etapa
        etapa = valor

    try:
        return executar_fluxo(registrar_etapa)
    except Exception as erro:
        mensagem = montar_payload(etapa, erro, execucao_id, time.monotonic() - inicio, (SENHA,))["mensagem"]
        print(f"[ERRO] {etapa}: {mensagem}", file=sys.stderr)
        enviar_relatorio(etapa, erro, execucao_id, time.monotonic() - inicio, segredos=(SENHA,))
        return 1


def executar_fluxo(registrar_etapa):
    print(" INICIANDO ROBÔ")
    print("="*60)

    # ETAPA 1: download do .jsp
    print("\n ETAPA 1: Download do .jsp")
    print("-"*60)
    registrar_etapa("download")
    baixar_jsp(download_dir=str(DOWNLOAD_DIR))

    # ETAPA 2: abre o .jsp e trata advertência Java
    print("\n ETAPA 2: Abrindo aplicação Java")
    print("-"*60)
    registrar_etapa("abertura_java")
    if not abrir_ultimo_jsp(pasta_downloads=DOWNLOAD_DIR):
        raise RuntimeError("Nenhum launcher encontrado para abrir o iBroker.")

    # ETAPA 3: login no i-Global
    print("\n ETAPA 3: Login no sistema")
    print("-"*60)
    registrar_etapa("login")
    if not executar_login(USUARIO, SENHA, propagar_erro=True):
        raise RuntimeError(" Login falhou. Abortando robô.")

    # ETAPA 4: atualização NCM
    #print("\n ETAPA 4: Atualização NCM")
    #print("-"*60)
    #executar_atualizacao_ncm()

    #print("\n ROBÔ FINALIZADO COM SUCESSO!")
    print("\n[PRONTO] iBroker aberto na tela inicial. A sessão permanece aberta para o próximo RPA.")
    return 0

if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
