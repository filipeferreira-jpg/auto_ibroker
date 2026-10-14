import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

import main
from bridge_client import ErroBridge
import relatorio_erros


class RelatoriosTest(unittest.TestCase):
    def test_senha_nao_aparece_no_payload(self):
        payload = relatorio_erros.montar_payload("login", ErroBridge("LOGIN_BLOQUEADO", "Falhou: senha-de-teste"), "execucao", 3.4, ("senha-de-teste",))
        self.assertNotIn("senha-de-teste", json.dumps(payload))
        self.assertEqual(payload["codigo"], "LOGIN_BLOQUEADO")
        self.assertFalse(payload["teste"])

    def test_envio_json_para_endpoint_configurado(self):
        with tempfile.TemporaryDirectory() as pasta, patch.object(relatorio_erros, "LOG_DIR", Path(pasta)), patch.object(relatorio_erros.requests, "post", return_value=Mock(status_code=204)) as post:
            self.assertTrue(relatorio_erros.enviar_relatorio("login", RuntimeError("teste"), "execucao"))
            self.assertEqual(post.call_args.args[0], relatorio_erros.WEBHOOK_ERROS)
            self.assertFalse(post.call_args.kwargs["allow_redirects"])
            self.assertEqual(post.call_args.kwargs["json"]["execucao_id"], "execucao")
            registro = json.loads((Path(pasta) / "erros_acesso.jsonl").read_text())
            self.assertTrue(registro["enviado"])

    def test_indisponibilidade_preserva_erro_local(self):
        with tempfile.TemporaryDirectory() as pasta, patch.object(relatorio_erros, "LOG_DIR", Path(pasta)), patch.object(relatorio_erros.requests, "post", side_effect=requests.Timeout("timeout")):
            self.assertFalse(relatorio_erros.enviar_relatorio("login", ErroBridge("LOGIN_TIMEOUT", "Janela ausente"), "execucao"))
            registro = json.loads((Path(pasta) / "erros_acesso.jsonl").read_text())
            self.assertEqual(registro["payload"]["codigo"], "LOGIN_TIMEOUT")
            self.assertEqual(registro["falha_envio"], "Timeout")

    def test_http_404_nao_e_entrega_confirmada(self):
        with tempfile.TemporaryDirectory() as pasta, patch.object(relatorio_erros, "LOG_DIR", Path(pasta)), patch.object(relatorio_erros.requests, "post", return_value=Mock(status_code=404)):
            self.assertFalse(relatorio_erros.enviar_relatorio("login", RuntimeError("teste")))
            registro = json.loads((Path(pasta) / "erros_acesso.jsonl").read_text())
            self.assertEqual(registro["http_status"], 404)
            self.assertFalse(registro["enviado"])


class FluxoTest(unittest.TestCase):
    def test_login_falho_reporta_codigo_original_e_aborta(self):
        erro = ErroBridge("LOGIN_BLOQUEADO", "Acesso rejeitado")
        with patch.object(main, "baixar_jsp"), patch.object(main, "abrir_ultimo_jsp", return_value=True), patch.object(main, "executar_login", side_effect=erro), patch.object(main, "enviar_relatorio") as enviar:
            self.assertEqual(main.main(), 1)
            self.assertEqual(enviar.call_args.args[0], "login")
            self.assertIs(enviar.call_args.args[1], erro)

    def test_download_falho_nao_abre_java(self):
        with patch.object(main, "baixar_jsp", side_effect=OSError("download falhou")), patch.object(main, "abrir_ultimo_jsp") as abrir, patch.object(main, "enviar_relatorio") as enviar:
            self.assertEqual(main.main(), 1)
            abrir.assert_not_called()
            self.assertEqual(enviar.call_args.args[0], "download")

    def test_launcher_ausente_nao_tenta_login(self):
        with patch.object(main, "baixar_jsp"), patch.object(main, "abrir_ultimo_jsp", return_value=False), patch.object(main, "executar_login") as login, patch.object(main, "enviar_relatorio") as enviar:
            self.assertEqual(main.main(), 1)
            login.assert_not_called()
            self.assertEqual(enviar.call_args.args[0], "abertura_java")

    def test_fluxo_bem_sucedido_nao_envia_erro(self):
        with patch.object(main, "baixar_jsp"), patch.object(main, "abrir_ultimo_jsp", return_value=True), patch.object(main, "executar_login", return_value=True), patch.object(main, "enviar_relatorio") as enviar:
            self.assertEqual(main.main(), 0)
            enviar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
