# Buduje OmniTV i instalator Windows (uruchamiaj w PowerShell na Windows).
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $python = $pythonCommand.Source }
}
if (-not (Test-Path $python)) {
    throw "Nie znaleziono Pythona. Zainstaluj Python 3.13 x64 lub utworz .venv."
}
& $python --version
if ($LASTEXITCODE -ne 0) { throw "Nie mozna uruchomic Pythona: $python" }

$mpvDll = Join-Path $root "libmpv-2.dll"
if (-not (Test-Path $mpvDll)) {
    throw "Brak wymaganego libmpv-2.dll w $root. Skopiuj DLL przed budowaniem."
}

& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Aktualizacja pip nie powiodla sie." }
& $python -m pip install -r requirements.txt pyinstaller
if ($LASTEXITCODE -ne 0) { throw "Instalacja zaleznosci nie powiodla sie." }
& $python -m PyInstaller --clean --noconfirm packaging\omnity.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller zakonczyl sie bledem $LASTEXITCODE." }

$dist = Join-Path $root "dist\OmniTV"
if (-not (Test-Path (Join-Path $dist "OmniTV.exe"))) {
    throw "PyInstaller nie utworzyl pliku $dist\OmniTV.exe."
}
Write-Host "Zbudowano aplikacje: $dist\OmniTV.exe"

Copy-Item $mpvDll (Join-Path $dist "libmpv-2.dll") -Force
Write-Host "Dolaczono: libmpv-2.dll"

$ffmpegSource = Join-Path $root "ffmpeg.exe"
if (-not (Test-Path $ffmpegSource)) {
    $ffmpegCommand = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
    if ($ffmpegCommand -and (Test-Path $ffmpegCommand.Source)) {
        $ffmpegSource = $ffmpegCommand.Source
    }
}
if (-not (Test-Path $ffmpegSource)) {
    $downloadDir = Join-Path $root "build\ffmpeg-download"
    New-Item -ItemType Directory -Force $downloadDir | Out-Null
    $downloadedFfmpeg = Get-ChildItem $downloadDir -Recurse -Filter "ffmpeg.exe" |
        Select-Object -First 1
    if (-not $downloadedFfmpeg) {
        $archive = Join-Path $downloadDir "ffmpeg-essentials.zip"
        Write-Host "Pobieranie FFmpeg potrzebnego do nagrywania..."
        Invoke-WebRequest `
            -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" `
            -OutFile $archive
        Expand-Archive -LiteralPath $archive -DestinationPath $downloadDir -Force
        $downloadedFfmpeg = Get-ChildItem $downloadDir -Recurse -Filter "ffmpeg.exe" |
            Select-Object -First 1
    }
    if (-not $downloadedFfmpeg) {
        throw "Pobrane archiwum FFmpeg nie zawiera ffmpeg.exe."
    }
    $ffmpegSource = $downloadedFfmpeg.FullName
}

& $ffmpegSource -version *> $null
if ($LASTEXITCODE -ne 0) { throw "Nie mozna uruchomic FFmpeg: $ffmpegSource" }
Copy-Item $ffmpegSource (Join-Path $dist "ffmpeg.exe") -Force
Write-Host "Dolaczono FFmpeg do nagrywania: $ffmpegSource"

if (-not (Test-Path (Join-Path $dist "ffmpeg.exe"))) {
    throw "Nie dolaczono ffmpeg.exe do aplikacji; nagrywanie nie bedzie dzialac."
}

$isccPath = $null
$isccCommand = Get-Command iscc -ErrorAction SilentlyContinue
if ($isccCommand) { $isccPath = $isccCommand.Source }
if (-not $isccPath) {
    $candidates = @(
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { $isccPath = $candidate; break }
    }
}

if ($isccPath) {
    & $isccPath (Join-Path $root "packaging\windows\installer.iss")
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup zakonczyl sie bledem $LASTEXITCODE" }
    $installer = Join-Path $root "dist\OmniTV-Setup-0.2.0.exe"
    if (-not (Test-Path $installer)) {
        throw "Inno Setup nie utworzyl instalatora: $installer"
    }
    Write-Host "Instalator: $root\dist\OmniTV-Setup-0.2.0.exe"
} else {
    Write-Warning "Aplikacja jest gotowa, ale instalator EXE nie zostal utworzony: brak Inno Setup 6 (ISCC.exe)."
    Write-Host "Zainstaluj Inno Setup i uruchom ponownie albo skompiluj packaging\windows\installer.iss recznie."
}
