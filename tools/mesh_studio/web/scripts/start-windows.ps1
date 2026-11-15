# Use the official Windows Python rather than the MSYS2/UCRT64 interpreter.
# Invoke from PowerShell or MSYS2: powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/mesh_studio/web/scripts/start-windows.ps1
param([switch]$SetupOnly, [switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$web = Join-Path $root 'tools\mesh_studio\web'
$venv = Join-Path $web '.venv-science'
$python = Join-Path $venv 'Scripts\python.exe'

if (-not (Test-Path $python)) {
    $launcher = Get-Command 'py.exe' -ErrorAction SilentlyContinue
    if (-not $launcher) {
        throw 'Install Python 3.13 for Windows (python.org) with the Python launcher. MSYS2/UCRT64 Python is not supported for this environment.'
    }
    $selected = (& $launcher.Source -3.13 -c 'import sys; print(sys.executable)').Trim()
    if ($LASTEXITCODE -ne 0 -or $selected -match '(?i)msys64|mingw|ucrt64') {
        throw 'Python 3.13 for Windows was not found. The MSYS2 interpreter must not be used.'
    }
    Write-Host "Creating isolated scientific environment using $selected"
    & $launcher.Source -3.13 -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create the virtual environment.' }
}
if (-not (Test-Path $python)) { throw 'Virtual environment python.exe is missing.' }
$interpreter = (& $python -c 'import sys; print(sys.executable)').Trim()
if ($LASTEXITCODE -ne 0 -or $interpreter -match '(?i)msys64|mingw|ucrt64') {
    throw 'Unexpected Python interpreter. Refusing to install into MSYS2.'
}
if (-not $SkipInstall) {
    & $python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
    & $python -m pip install -r (Join-Path $root 'tools\mesh_studio\requirements-web-ci.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Scientific dependency installation failed.' }
}
$node = Get-Command 'node.exe' -ErrorAction SilentlyContinue
$npm = Get-Command 'npm.cmd' -ErrorAction SilentlyContinue
if (-not $node -or -not $npm) { throw 'Node.js 22 and npm.cmd are required. Install Node.js for Windows.' }
if (-not (Test-Path (Join-Path $web 'node_modules'))) {
    Push-Location $web
    try {
        & $npm.Source install --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    } finally { Pop-Location }
}
if ($SetupOnly) {
    Write-Host "Ready. Python: $python"
    Write-Host 'Start the backend and frontend using two PowerShell sessions or rerun this script without -SetupOnly.'
    exit 0
}
# Both servers bind to loopback only; never expose a research service to the network.
$api = Start-Process -FilePath $python -WorkingDirectory $root -PassThru -ArgumentList @('-m','uvicorn','tools.mesh_studio.web_api:app','--host','127.0.0.1','--port','8765')
Start-Sleep -Seconds 2
if ($api.HasExited) { throw 'Scientific API exited. Run uvicorn manually to inspect its diagnostics.' }
$frontend = Start-Process -FilePath $npm.Source -WorkingDirectory $web -PassThru -ArgumentList @('run','dev')
Write-Host "Scientific API PID: $($api.Id) | Web frontend PID: $($frontend.Id)"
Write-Host 'Open http://127.0.0.1:5173 and http://127.0.0.1:8765/api/docs'
Write-Host 'Close the two processes when finished. The original APMesh generator is not started.'
