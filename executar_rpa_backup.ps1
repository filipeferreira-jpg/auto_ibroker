$ErrorActionPreference = 'Stop'

$maxTentativas = 3
$intervaloSegundos = 120
$codigoTimeoutJava = 20 # Codigo de saida do main.py para ABERTURA_JAVA_TIMEOUT.
$id = '{0}_{1}' -f (Get-Date -Format 'yyyyMMdd_HHmmss'), ([guid]::NewGuid().ToString('N'))
$pastaLogs = Join-Path $PSScriptRoot "logs\abertura_backup\$id"
$diasRetencao = 14
$pastaBase = Join-Path $PSScriptRoot 'logs\abertura_backup'
foreach ($pasta in @((Split-Path -Parent $pastaBase), $pastaBase)) {
    if (Test-Path -LiteralPath $pasta) {
        $item = Get-Item -LiteralPath $pasta -Force
        if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Caminho de logs invalido: $pasta"
        }
    }
}
New-Item -ItemType Directory -Path $pastaLogs | Out-Null
$resumo = Join-Path $pastaLogs 'resumo.log'

function Registrar($mensagem) {
    $linha = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'), $mensagem
    Add-Content -LiteralPath $resumo -Value $linha -Encoding UTF8
    Write-Host $linha
}

Registrar "Logs em $pastaLogs"

try {
    $limite = (Get-Date).AddDays(-$diasRetencao)
    $baseAbsoluta = (Resolve-Path -LiteralPath $pastaBase).ProviderPath
    $removidas = 0
    foreach ($antiga in Get-ChildItem -LiteralPath $baseAbsoluta -Directory) {
        if ($antiga.Name -notmatch '^\d{8}_\d{6}_[a-f0-9]{32}$' -or
            $antiga.LastWriteTime -ge $limite -or
            ($antiga.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
            $antiga.Parent.FullName -ne $baseAbsoluta) { continue }
        try {
            $arquivos = @(Get-ChildItem -LiteralPath $antiga.FullName -Force)
            if ($arquivos | Where-Object {
                $_.PSIsContainer -or
                ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
                $_.Name -notmatch '^(resumo\.log|tentativa-[1-3]\.(stdout|stderr)\.log)$'
            }) { continue }
            foreach ($arquivo in $arquivos) { Remove-Item -LiteralPath $arquivo.FullName }
            [IO.Directory]::Delete($antiga.FullName)
            $removidas++
        } catch {
            Registrar "Falha ao limpar $($antiga.Name): $($_.Exception.Message)"
        }
    }
    Registrar "Retencao: $diasRetencao dias. Pastas removidas: $removidas."
} catch {
    Registrar "Falha na limpeza de logs: $($_.Exception.Message)"
}
for ($tentativa = 1; $tentativa -le $maxTentativas; $tentativa++) {
    $stdout = "logs\abertura_backup\$id\tentativa-$tentativa.stdout.log"
    $stderr = "logs\abertura_backup\$id\tentativa-$tentativa.stderr.log"
    Registrar "Tentativa $tentativa/$maxTentativas iniciada. Saidas: $stdout e $stderr"
    Push-Location -LiteralPath $PSScriptRoot
    try {
        & $env:ComSpec /d /c "executar_rpa.bat 1>$stdout 2>$stderr"
        $codigo = $LASTEXITCODE
    } catch {
        Registrar "Falha ao executar o BAT: $($_.Exception.Message)"
        exit 1
    } finally {
        Pop-Location
    }

    if ($codigo -eq 0) {
        Registrar "Tentativa $tentativa concluida com sucesso (codigo 0)."
        exit 0
    }
    if ($codigo -ne $codigoTimeoutJava) {
        Registrar "Tentativa $tentativa falhou com codigo $codigo. Encerrando."
        exit $codigo
    }

    Registrar "Tentativa $tentativa falhou com ABERTURA_JAVA_TIMEOUT (codigo $codigo)."
    if ($tentativa -lt $maxTentativas) {
        Registrar "Aguardando $intervaloSegundos segundos antes da proxima tentativa."
        Start-Sleep -Seconds $intervaloSegundos
    }
}
Registrar "Limite de $maxTentativas tentativas atingido."
exit $codigoTimeoutJava
