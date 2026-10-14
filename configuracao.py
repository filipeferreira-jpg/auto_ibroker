"""Credenciais locais; variáveis do ambiente prevalecem sobre o arquivo .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

USUARIO = os.environ.get("IBROKER_USUARIO", "")
SENHA = os.environ.get("IBROKER_SENHA", "")
