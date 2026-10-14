"""Relatórios de falhas enviados ao n8n, sem credenciais ou screenshots."""
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import socket
from uuid import uuid4

import requests

WEBHOOK_ERROS = "https://n8n2.titoonline.com.br/webhook/retorno_erro"
LOG_DIR = Path(__file__).resolve().parent / "logs"


def montar_payload(etapa, erro, execucao_id, duracao_segundos, segredos=(), teste=False):
    mensagem = str(erro).split("\nStacktrace:", 1)[0]
    for segredo in segredos:
        if segredo:
            mensagem = mensagem.replace(segredo, "[REMOVIDO]")
    return {
        "schema_version": 1,
        "teste": teste,
        "evento": "erro_acesso_ibroker",
        "aplicacao": "auto_ibroker",
        "rpa": os.environ.get("IBROKER_RPA", "abertura_ibroker"),
        "execucao_id": execucao_id,
        "maquina": socket.gethostname(),
        "data_hora": datetime.now().astimezone().isoformat(timespec="seconds"),
        "etapa": etapa,
        "codigo": getattr(erro, "codigo", "ERRO_" + etapa.upper()),
        "tipo_erro": type(erro).__name__,
        "mensagem": mensagem[:2000],
        "duracao_segundos": round(duracao_segundos, 2),
    }


def enviar_relatorio(etapa, erro, execucao_id=None, duracao_segundos=0, segredos=(), teste=False):
    payload = montar_payload(etapa, erro, execucao_id or str(uuid4()), duracao_segundos, segredos, teste)
    registro = {"payload": payload, "enviado": False}
    try:
        resposta = requests.post(WEBHOOK_ERROS, json=payload, timeout=(5, 10), allow_redirects=False)
        registro["http_status"] = resposta.status_code
        if not 200 <= resposta.status_code < 300:
            raise requests.HTTPError(f"Webhook respondeu HTTP {resposta.status_code}")
        registro["enviado"] = True
    except requests.RequestException as exc:
        # Não imprimir corpo da resposta, URLs de proxy ou credenciais.
        registro["falha_envio"] = type(exc).__name__
        logging.error("Não foi possível entregar o relatório ao n8n (%s).", type(exc).__name__)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with (LOG_DIR / "erros_acesso.jsonl").open("a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except OSError:
        logging.error("Não foi possível gravar o relatório local de erro.")
    return registro["enviado"]
