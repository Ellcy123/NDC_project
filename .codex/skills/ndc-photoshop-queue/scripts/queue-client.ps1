param(
    [Parameter(Mandatory = $true)]
    [string]$Task,

    [string]$Action,

    [string]$Request
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Action) -eq [string]::IsNullOrWhiteSpace($Request)) {
    throw 'Specify exactly one of -Action or -Request.'
}

$nodeExe = $null
if (-not [string]::IsNullOrWhiteSpace($env:NDC_NODE_EXE)) {
    if (-not [IO.Path]::IsPathFullyQualified($env:NDC_NODE_EXE) -or -not (Test-Path -LiteralPath $env:NDC_NODE_EXE -PathType Leaf)) {
        throw 'NDC_NODE_EXE must name an existing absolute Node executable.'
    }
    $nodeExe = (Resolve-Path -LiteralPath $env:NDC_NODE_EXE).Path
} else {
    $nodeCommand = Get-Command node -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($nodeCommand) {
        $nodeExe = $nodeCommand.Source
    } else {
        $bundledNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
        if (Test-Path -LiteralPath $bundledNode -PathType Leaf) {
            $nodeExe = (Resolve-Path -LiteralPath $bundledNode).Path
        }
    }
}

if (-not $nodeExe) {
    throw 'Node.js is required. Install it or set NDC_NODE_EXE to an existing absolute node.exe.'
}

$client = Join-Path $PSScriptRoot 'queue-client.mjs'
$arguments = @($client, '--task', $Task)
if ($Action) {
    $arguments += @('--action', $Action)
} else {
    $arguments += @('--request', (Resolve-Path -LiteralPath $Request).Path)
}

& $nodeExe @arguments
exit $LASTEXITCODE
