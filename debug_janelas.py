import time
from pywinauto import Desktop

def listar_janelas_por_30s(segundos=30):
    fim = time.time() + segundos
    while time.time() < fim:
        wins = Desktop(backend="uia").windows()
        titulos = sorted({(w.window_text() or "").strip() for w in wins if (w.window_text() or "").strip()})
        print("\n--- JANELAS (amostra) ---")
        for t in titulos[:60]:
            print(t)
        time.sleep(2)

listar_janelas_por_30s(30)