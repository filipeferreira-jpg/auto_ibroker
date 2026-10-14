import os
import time
from pathlib import Path
from datetime import datetime

from java_watcher import aguardar_fluxo_java


def abrir_ultimo_jsp(pasta_downloads: Path | None = None, padrao: str = "*.jsp") -> bool:
    downloads = pasta_downloads or (Path.home() / "Downloads")

    arquivos = list(downloads.glob(padrao))
    if not arquivos:
        print(f"Nenhum arquivo encontrado em {downloads} com padrão {padrao}")
        return False

    ultimo = max(arquivos, key=lambda p: p.stat().st_mtime)
    mtime = datetime.fromtimestamp(ultimo.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

    print(f"Abrindo o arquivo mais recente: {ultimo.name}")
    print(f"Caminho: {ultimo}")
    print(f"Modificado em: {mtime}")

    os.startfile(str(ultimo))

    # respiro para o launcher criar janelas
    time.sleep(1)

    status = aguardar_fluxo_java(timeout=90) 

    if status == "warning":
        print(" Advertência tratada pelo Bridge: checkbox marcado e ação Executar enviada.")
    elif status == "login":
        print("[JAVA] Janela de login disponível sem advertência.")
    print("[JAVA] Seguindo para login pelo Bridge…")
    return True


if __name__ == "__main__":
    abrir_ultimo_jsp()
