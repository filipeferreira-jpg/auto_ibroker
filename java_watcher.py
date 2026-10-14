"""Abertura e login Java por controles acessíveis, sem OCR ou coordenadas."""
from bridge_client import executar_bridge

TITLE_WARNING = "Advertência de Segurança"
TITLE_LOADING = "Iniciando aplicativo..."
TITLE_LOGIN = "i-Global"


def aguardar_fluxo_java(timeout=60):
    print("[JAVA] Aguardando o launcher pelo Java Access Bridge...")
    resultado = executar_bridge("warning", timeout=timeout)
    return resultado["status"]


def realizar_login(usuario: str, senha: str):
    print("[LOGIN] Aguardando e preenchendo controles pelo Java Access Bridge...")
    resultado = executar_bridge("login", timeout=60, usuario=usuario, senha=senha)
    print(f"[LOGIN] Tela inicial confirmada: {resultado['title']}")
    return resultado
