import time
import pyautogui
# pyrefly: ignore [missing-import]
from pywinauto import Desktop

TITLE_WARNING = "Advertência de Segurança"
TITLE_LOADING = "Iniciando aplicativo..."
TITLE_LOGIN   = "i-Global"

def _get_win(title: str):
    return Desktop(backend="uia").window(title=title)

# ============================================================
# ADVERTÊNCIA DE SEGURANÇA JAVA
# ============================================================

def tratar_advertencia(w_warning):
    rect = w_warning.rectangle()
    print(f"[JAVA] Janela em: left={rect.left} top={rect.top} right={rect.right} bottom={rect.bottom}")

    # AÇÃO 1: checkbox 'Eu aceito o risco e desejo executar este aplicativo'
    x_checkbox = rect.left + 40
    y_checkbox = rect.bottom - 36
    print(f"[JAVA] Ação 1: Clicando no checkbox em ({x_checkbox}, {y_checkbox})")
    pyautogui.click(x_checkbox, y_checkbox)
    time.sleep(1)
    print(" Checkbox clicado!")

    # AÇÃO 2: botão 'Executar'
    x_executar = rect.right - 148
    y_executar = rect.bottom - 36
    print(f"[JAVA] Ação 2: Clicando em 'Executar' em ({x_executar}, {y_executar})")
    pyautogui.click(x_executar, y_executar)
    time.sleep(2)
    print(" 'Executar' clicado!")

def aguardar_fluxo_java(timeout=60):
    start = time.time()
    last_log = 0
    viu_loading = False

    while time.time() - start < timeout:
        w_loading = _get_win(TITLE_LOADING)
        w_warning = _get_win(TITLE_WARNING)

        loading_vis = w_loading.exists(timeout=0.2) and w_loading.is_visible()
        warning_vis = w_warning.exists(timeout=0.2) and w_warning.is_visible()

        if loading_vis:
            viu_loading = True

        if warning_vis:
            try:
                w_warning.set_focus()
            except Exception:
                pass
            print("[JAVA] Advertência detectada! Executando ações...")
            tratar_advertencia(w_warning)
            return "warning"

        if time.time() - last_log >= 2:
            print(
                f"[JAVA] t={int(time.time()-start)}s | loading={loading_vis} | warning={warning_vis} | viu_loading={viu_loading}"
            )
            last_log = time.time()

        time.sleep(0.25)

    return "none"

# ============================================================
# LOGIN NO SISTEMA
# ============================================================

def aguardar_janela_login(timeout=60):
    start = time.time()
    last_log = 0

    while time.time() - start < timeout:
        try:
            # busca por título parcial com regex
            w = Desktop(backend="uia").window(title_re=".*i-Global.*")
            if w.exists(timeout=0.2) and w.is_visible():
                print("[LOGIN]  Janela de login detectada!")
                return w
        except Exception:
            pass

        if time.time() - last_log >= 2:
            print(f"[LOGIN] t={int(time.time()-start)}s | Aguardando janela de login...")
            last_log = time.time()

        time.sleep(0.5)

    raise RuntimeError(" Janela de login não apareceu dentro do timeout.")


def realizar_login(usuario: str, senha: str):
    w = aguardar_janela_login(timeout=60)

    try:
        w.set_focus()
    except Exception:
        pass

    rect = w.rectangle()
    print(f"[LOGIN] Janela em: left={rect.left} top={rect.top} right={rect.right} bottom={rect.bottom}")

    # --- CAMPO USUÁRIO ---
    try:
        campo = w.child_window(title="Usuário", control_type="Edit")
        campo.wait("visible", timeout=5)
        campo.set_edit_text(usuario)
        print(" Usuário preenchido via pywinauto!")
    except Exception as e:
        print(f" pywinauto falhou no campo Usuário ({e}), usando pyautogui...")
        x = rect.left + int((rect.right - rect.left) * 0.62)
        y = rect.top  + int((rect.bottom - rect.top)  * 0.42)
        pyautogui.click(x, y)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.typewrite(usuario, interval=0.05)
        print(" Usuário preenchido via pyautogui!")

    time.sleep(0.3)

    # --- CAMPO SENHA ---
    try:
        campo = w.child_window(title="Senha", control_type="Edit")
        campo.wait("visible", timeout=5)
        campo.set_edit_text(senha)
        print(" Senha preenchida via pywinauto!")
    except Exception as e:
        print(f" pywinauto falhou no campo Senha ({e}), usando pyautogui...")
        x = rect.left + int((rect.right - rect.left) * 0.62)
        y = rect.top  + int((rect.bottom - rect.top)  * 0.55)
        pyautogui.click(x, y)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.typewrite(senha, interval=0.05)
        print(" Senha preenchida via pyautogui!")

    time.sleep(0.3)

    # --- BOTÃO LOGIN ---
    try:
        btn = w.child_window(title="Login", control_type="Button")
        btn.wait("enabled", timeout=5)
        btn.click()
        print(" Botão 'Login' clicado via pywinauto!")
    except Exception as e:
        print(f" pywinauto falhou no botão Login ({e}), usando pyautogui...")
        x = rect.left + int((rect.right - rect.left) * 0.75)
        y = rect.top  + int((rect.bottom - rect.top)  * 0.68)
        pyautogui.click(x, y)
        print("Botão 'Login' clicado via pyautogui!")

    time.sleep(3)
    print(" Login realizado com sucesso!")