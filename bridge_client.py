"""Cliente Python para o auxiliar Java Access Bridge de 32 bits."""
import json
import os
from pathlib import Path
import subprocess


class ErroBridge(RuntimeError):
    def __init__(self, codigo, mensagem):
        super().__init__(mensagem)
        self.codigo = codigo


def executar_bridge(comando, timeout=60, **parametros):
    raiz = Path(__file__).resolve().parent
    host = Path(os.environ.get("WINDIR", r"C:\Windows")) / "SysWOW64" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if not host.exists():
        raise ErroBridge("HOST_BRIDGE_AUSENTE", "O host PowerShell de 32 bits não foi encontrado.")
    try:
        resultado = subprocess.run(
            [str(host), "-NoProfile", "-NonInteractive", "-STA", "-File", str(raiz / "native" / "run_bridge.ps1")],
            input=json.dumps({"command": comando, "timeout": timeout, **parametros}, ensure_ascii=False),
            capture_output=True, encoding="utf-8", errors="replace", timeout=timeout + 15,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except subprocess.TimeoutExpired as exc:
        raise ErroBridge("BRIDGE_TIMEOUT", "O auxiliar Bridge excedeu o prazo de execução.") from exc
    except OSError as exc:
        raise ErroBridge("BRIDGE_INDISPONIVEL", "Não foi possível iniciar o auxiliar Bridge.") from exc
    try:
        resposta = json.loads(resultado.stdout.lstrip("\ufeff"))
    except (ValueError, TypeError) as exc:
        raise ErroBridge("RESPOSTA_BRIDGE_INVALIDA", "Resposta inválida do auxiliar Bridge.") from exc
    if not resposta.get("ok") or resultado.returncode:
        raise ErroBridge(resposta.get("code", "BRIDGE_FALHOU"), resposta.get("message", "Falha no Bridge."))
    return resposta


if __name__ == "__main__":
    print(json.dumps(executar_bridge("inspect"), ensure_ascii=False, indent=2))
