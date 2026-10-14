$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$pedidoBridge = [Console]::In.ReadToEnd()
try {
    Add-Type -Path (Join-Path $PSScriptRoot 'JavaBridgeHost.cs') -ReferencedAssemblies 'System.dll', 'System.Core.dll', 'System.Windows.Forms.dll', 'System.Web.Extensions.dll'
    $resultadoBridge = [JavaBridgeHost]::Run($pedidoBridge)
    exit $resultadoBridge
} catch {
    [Console]::Out.WriteLine('{"ok":false,"code":"HOST_BRIDGE_FALHOU","message":"Falha ao carregar o adaptador Java Access Bridge no host de 32 bits."}')
    exit 1
}
