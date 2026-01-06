#!/usr/bin/env pwsh

param(
    [string]$PythonBin = $null
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $PythonBin) {
    if ($env:VIRTUAL_ENV) {
        $venvPython = Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe'
        if (Test-Path $venvPython) {
            $PythonBin = $venvPython
        }
    }
}

if (-not $PythonBin) {
    $PythonBin = 'python.exe'
}

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot '..')

Push-Location $projectRoot
try {
    & $PythonBin manage.py makemessages -v 0 --no-wrap --no-obsolete -l pl '--ignore=.git/*' '--ignore=static/*' '--ignore=.mypy_cache/*'
    & $PythonBin manage.py compilemessages -v 0 '--ignore=.git/*' '--ignore=static/*' '--ignore=.mypy_cache/*'
}
finally {
    Pop-Location
}