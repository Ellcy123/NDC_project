[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [Parameter(Mandatory = $true)]
    [string]$BaseName,

    [Parameter(Mandatory = $true)]
    [string]$Points,

    [ValidateRange(1, 256)]
    [int]$BorderWidth = 18
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) {
    throw "Input image does not exist: $InputPath"
}

if ([System.IO.Path]::GetExtension($InputPath) -ne '.png') {
    throw 'Input image must be a PNG.'
}

if ([string]::IsNullOrWhiteSpace($BaseName)) {
    throw 'BaseName cannot be empty.'
}

Add-Type -AssemblyName System.Drawing

$culture = [System.Globalization.CultureInfo]::InvariantCulture
$numberStyle = [System.Globalization.NumberStyles]::Float
$normalizedPoints = @()

foreach ($pointToken in $Points.Split(';', [System.StringSplitOptions]::RemoveEmptyEntries)) {
    $pair = $pointToken.Split(',')
    if ($pair.Count -ne 2) {
        throw "Invalid point '$pointToken'. Expected normalized x,y."
    }

    $x = [double]::Parse($pair[0].Trim(), $numberStyle, $culture)
    $y = [double]::Parse($pair[1].Trim(), $numberStyle, $culture)
    if ($x -lt 0 -or $x -gt 1 -or $y -lt 0 -or $y -gt 1) {
        throw "Point '$pointToken' is outside the normalized 0..1 range."
    }

    $normalizedPoints += [pscustomobject]@{ X = $x; Y = $y }
}

if ($normalizedPoints.Count -lt 3) {
    throw 'At least three polygon points are required.'
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$rgbaPath = Join-Path $OutputDirectory ($BaseName + '_panel_rgba.png')
$magentaPath = Join-Path $OutputDirectory ($BaseName + '_magenta_mask.png')

foreach ($outputPath in @($rgbaPath, $magentaPath)) {
    if (Test-Path -LiteralPath $outputPath) {
        throw "Refusing to overwrite existing output: $outputPath"
    }
}

$source = [System.Drawing.Bitmap]::FromFile($InputPath)
try {
    $width = $source.Width
    $height = $source.Height
    $pixelPoints = [System.Drawing.Point[]]@(
        $normalizedPoints | ForEach-Object {
            [System.Drawing.Point]::new(
                [int][Math]::Round($_.X * ($width - 1)),
                [int][Math]::Round($_.Y * ($height - 1))
            )
        }
    )

    $polygon = [System.Drawing.Drawing2D.GraphicsPath]::new()
    try {
        $polygon.AddPolygon($pixelPoints)

        $targets = @(
            [pscustomobject]@{ Path = $rgbaPath; Transparent = $true },
            [pscustomobject]@{ Path = $magentaPath; Transparent = $false }
        )

        foreach ($target in $targets) {
            $canvas = [System.Drawing.Bitmap]::new(
                $width,
                $height,
                [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
            )
            try {
                $graphics = [System.Drawing.Graphics]::FromImage($canvas)
                try {
                    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
                    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

                    if ($target.Transparent) {
                        $graphics.Clear([System.Drawing.Color]::Transparent)
                    }
                    else {
                        $graphics.Clear([System.Drawing.Color]::Magenta)
                    }

                    $graphics.SetClip($polygon)
                    $graphics.DrawImage($source, 0, 0, $width, $height)
                    $graphics.ResetClip()

                    $pen = [System.Drawing.Pen]::new([System.Drawing.Color]::Black, $BorderWidth)
                    try {
                        $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Miter
                        $graphics.DrawPath($pen, $polygon)
                    }
                    finally {
                        $pen.Dispose()
                    }
                }
                finally {
                    $graphics.Dispose()
                }

                $canvas.Save($target.Path, [System.Drawing.Imaging.ImageFormat]::Png)
            }
            finally {
                $canvas.Dispose()
            }
        }
    }
    finally {
        $polygon.Dispose()
    }
}
finally {
    $source.Dispose()
}

$check = [System.Drawing.Bitmap]::FromFile($rgbaPath)
try {
    $alpha = [ordered]@{
        topLeft = $check.GetPixel(0, 0).A
        topRight = $check.GetPixel($check.Width - 1, 0).A
        bottomLeft = $check.GetPixel(0, $check.Height - 1).A
        bottomRight = $check.GetPixel($check.Width - 1, $check.Height - 1).A
        center = $check.GetPixel([int]($check.Width / 2), [int]($check.Height / 2)).A
    }

    [pscustomobject]@{
        input = (Resolve-Path -LiteralPath $InputPath).Path
        rgba = (Resolve-Path -LiteralPath $rgbaPath).Path
        magenta = (Resolve-Path -LiteralPath $magentaPath).Path
        width = $check.Width
        height = $check.Height
        ratio = [Math]::Round($check.Width / $check.Height, 6)
        borderWidth = $BorderWidth
        normalizedPoints = $normalizedPoints
        alpha = $alpha
        inputSHA256 = (Get-FileHash -LiteralPath $InputPath -Algorithm SHA256).Hash
        rgbaSHA256 = (Get-FileHash -LiteralPath $rgbaPath -Algorithm SHA256).Hash
        magentaSHA256 = (Get-FileHash -LiteralPath $magentaPath -Algorithm SHA256).Hash
    } | ConvertTo-Json -Depth 6
}
finally {
    $check.Dispose()
}
