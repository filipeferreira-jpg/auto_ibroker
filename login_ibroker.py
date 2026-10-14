# ============================================================
# login_ibroker.py - Realiza login no i-Global
# ============================================================
from java_watcher import realizar_login
from configuracao import USUARIO, SENHA


def executar_login(usuario: str = USUARIO, senha: str = SENHA, propagar_erro: bool = False) -> bool:
    """
    Aguarda a janela de login do i-Global aparecer e realiza o login.
    Retorna True se o login foi executado com sucesso.
    """
    print("\n Realizando login no i-Global")
    print("-"*60)

    try:
        realizar_login(usuario, senha)
        print(" Login concluído com sucesso!")
        return True
    except RuntimeError as e:
        if propagar_erro:
            raise
        print(f" Falha no login: {e}")
        return False

if __name__ == "__main__":
    executar_login()
