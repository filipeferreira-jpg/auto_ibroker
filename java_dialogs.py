import time
import io
from pathlib import Path
from datetime import datetime

# pyrefly: ignore [missing-import]
from pywinauto import Desktop
from PIL import ImageGrab


def _tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _salvar_evidencias(pasta="logs_java"):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    tag = _tag()

    img_path = pasta / f"java_{tag}.png"
    ImageGrab.grab(all_screens=True).save(img_path)

    return img_path


def aguardar_janela_sumir(title_re: str, timeout: int = 40) -> bool:
    """
    Se a janela aparecer, espera ela sumir. Se não aparecer, retorna False.
    """
    start = time.time()
    viu = False

    while time.time() - start < timeout:
        w = Desktop(backend="uia").window(title_re=title_re)
        if w.exists(timeout=0.2) and w.is_visible():
            viu = True
            # espera desaparecer
            while w.exists(timeout=0.5) and w.is_visible():
                time.sleep(0.3)
            return True
        time.sleep(0.2)

    return viu


def detectar_janela(title_re: str, timeout: int = 20):
    start = time.time()
    while time.time() - start < timeout:
        dlg = Desktop(backend="uia").window(title_re=title_re)
        if dlg.exists(timeout=0.2) and dlg.is_visible():
            try:
                dlg.set_focus()
            except Exception:
                pass
            return dlg
        time.sleep(0.2)
    return None


def gate_java_pos_execucao(timeout_verificacao=40, timeout_advertencia=40, evidencias_dir="logs_java"):
    """
    - Aguarda (se existir) a janela de carregamento/verificação do Java
    - Procura a 'Advertência de Segurança'
    - Se achar, salva print e levanta exceção
    """
    loading_re = r".*(Iniciando aplicativo|Verificando o aplicativo|Starting application|Verifying application).*"
    warning_re = r".*(Advert[êe]ncia de Seguran[çc]a|Security Warning).*"

    print("[JAVA] Aguardando janela de verificação/carregamento (se aparecer)...")
    apareceu = aguardar_janela_sumir(loading_re, timeout=timeout_verificacao)
    print(f"[JAVA] Janela de verificação apareceu? {apareceu}")

    print("[JAVA] Procurando 'Advertência de Segurança'...")
    dlg = detectar_janela(warning_re, timeout=timeout_advertencia)
    if dlg is not None:
        img = _salvar_evidencias(pasta=evidencias_dir)
        raise RuntimeError(
            f"[JAVA] Advertência de Segurança detectada. Evidência salva em: {img}"
        )

    print("[JAVA] Nenhuma advertência detectada nesse período.")