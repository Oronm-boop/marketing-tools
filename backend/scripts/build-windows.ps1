$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendRoot = Resolve-Path (Join-Path $ScriptDir '..')
$Python = Join-Path $BackendRoot '.venv\Scripts\python.exe'
$Requirements = Join-Path $BackendRoot 'requirements.txt'
$Entry = Join-Path $BackendRoot 'run_backend.py'
$OutputExe = Join-Path $BackendRoot 'dist\mdt-ai-backend.exe'

if (-not (Test-Path $Python)) {
  py -m venv (Join-Path $BackendRoot '.venv')
}

& $Python -m pip install -r $Requirements
if ($LASTEXITCODE -ne 0) {
  throw "pip install requirements failed with exit code $LASTEXITCODE"
}

& $Python -m pip install 'pyinstaller>=6.16'
if ($LASTEXITCODE -ne 0) {
  throw "pip install pyinstaller failed with exit code $LASTEXITCODE"
}

Get-Process -Name 'mdt-ai-backend' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 300

if (Test-Path $OutputExe) {
  Remove-Item -LiteralPath $OutputExe -Force
}

Push-Location $BackendRoot
try {
  & $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --console `
    --name mdt-ai-backend `
    --paths $BackendRoot `
    $Entry
  if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}

if (-not (Test-Path $OutputExe)) {
  throw "Backend executable was not created: $OutputExe"
}

Write-Host "Backend executable created: $OutputExe"
