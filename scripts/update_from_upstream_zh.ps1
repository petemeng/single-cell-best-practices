param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Arguments -join ' ')"
    }
}

if (-not (git remote | Select-String -SimpleMatch "upstream")) {
    Invoke-Checked git remote add upstream https://github.com/theislab/single-cell-best-practices.git
}

$dirty = git status --porcelain
if ($dirty) {
    Write-Host "Working tree has uncommitted changes. Commit or stash them before updating from upstream." -ForegroundColor Yellow
    git status --short
    exit 1
}

Invoke-Checked git fetch upstream
Invoke-Checked git merge upstream/main

Invoke-Checked python scripts/translate_book_zh.py --force --sleep 0.02

if (-not $SkipBuild) {
    Invoke-Checked uv tool run --from jupyter-book==1.0.4.post1 --with jupytext==1.16.7 --with beautifulsoup4==4.13.3 --with sphinx==7.4.7 jupyter-book build jupyter-book-zh
}

git status --short
