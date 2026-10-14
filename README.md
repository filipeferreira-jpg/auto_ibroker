# Abertura do iBroker

Fluxo atual: download do launcher Export, execução Java, login e confirmação da
tela inicial. A aplicação fica aberta para o próximo RPA. A atualização de NCM
continua comentada em `main.py`.

## Execução

Antes da primeira execução, copie `.env.example` para `.env` e preencha
`IBROKER_USUARIO` e `IBROKER_SENHA`. O arquivo `.env` é local e ignorado pelo Git.
As mesmas variáveis podem ser fornecidas pelo ambiente do UiPath, sem arquivo;
valores definidos no ambiente prevalecem sobre `.env`.

```powershell
.\.venv\Scripts\python.exe main.py
```

O resultado é código de saída `0` quando a tela inicial é confirmada e `1` em
caso de falha. Não é necessário manter o Access Bridge Explorer aberto.

## Requisitos do Bridge

- Windows de 64 bits com Windows PowerShell de 32 bits e .NET Framework 4.
- Java de 32 bits com `WindowsAccessBridge-32.dll` instalado em SysWOW64.
- Java Access Bridge habilitado para o usuário que executa o RPA:

```powershell
& 'C:\Program Files (x86)\Java\jre1.8.0_341\bin\jabswitch.exe' -enable
```

Reinicie a aplicação Java depois de habilitar o Bridge. O host local compila
`native/JavaBridgeHost.cs` em memória para usar a DLL de 32 bits, enquanto o
Python permanece de 64 bits. Não instala software nem modifica políticas do
PowerShell. Se a máquina restringir scripts, a equipe deverá autorizar/assinar
`native/run_bridge.ps1` conforme sua configuração.

O login usa a janela i-Global do Export, os rótulos Usuário/Senha, um campo de
texto editável, um campo de senha e o botão Login. Controles ambíguos abortam a
execução. Não existe fallback para OCR ou coordenadas na abertura/login.
O sucesso exige a janela principal do mesmo processo, identificação de usuário,
menus Movimentação/Tabelas disponíveis e ausência de diálogo modal ou tela interna.
Não são repetidas tentativas de login após o envio do botão Login.

## Erros enviados ao n8n

O `main.py` envia um POST JSON para:

`https://n8n2.titoonline.com.br/webhook/retorno_erro`

O payload contém `schema_version`, `teste`, `evento`, `aplicacao`, `rpa`,
`execucao_id`, `maquina`, `data_hora`, `etapa`, `codigo`, `tipo_erro`, `mensagem`
e `duracao_segundos`. Não inclui senha, screenshot ou traceback.
O relatório e o resultado da entrega ficam em `logs/erros_acesso.jsonl`.
Se o webhook estiver indisponível, o erro original é preservado; não há reenvio
automático nem workflow criado por este projeto.

Configurações opcionais:

- `IBROKER_DOWNLOAD_DIR`: pasta de download; padrão é Downloads do usuário.
- `IBROKER_RPA`: identificador incluído no relatório; padrão `abertura_ibroker`.

Os módulos antigos de atualização/OCR permanecem no repositório, mas não são
importados nem executados por este fluxo. Os notebooks foram removidos.

## Verificação sem acessar o sistema

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
