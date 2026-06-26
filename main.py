# ============================================================
# main.py - Orquestrador principal do robô NCM
# ============================================================
from pathlib import Path

from acesso_ibroker import baixar_jsp
from executa_jsp    import abrir_ultimo_jsp
from login_ibroker  import executar_login 
#from atualiza_ncm   import executar_atualizacao_ncm


DOWNLOAD_DIR = Path.home() / "Downloads"
USUARIO      = "robo.expo"
SENHA        = "rp@123"

def main():
    print(" INICIANDO ROBÔ")
    print("="*60)

    # ETAPA 1: download do .jsp
    print("\n ETAPA 1: Download do .jsp")
    print("-"*60)
    baixar_jsp(download_dir=str(DOWNLOAD_DIR))

    # ETAPA 2: abre o .jsp e trata advertência Java
    print("\n ETAPA 2: Abrindo aplicação Java")
    print("-"*60)
    abrir_ultimo_jsp(pasta_downloads=DOWNLOAD_DIR)

    # ETAPA 3: login no i-Global
    print("\n ETAPA 3: Login no sistema")
    print("-"*60)
    if not executar_login(USUARIO, SENHA): 
        raise RuntimeError(" Login falhou. Abortando robô.")

    # ETAPA 4: atualização NCM
    #print("\n ETAPA 4: Atualização NCM")
    #print("-"*60)
    #executar_atualizacao_ncm()

    #print("\n ROBÔ FINALIZADO COM SUCESSO!")

if __name__ == "__main__":
    main()