$ErrorActionPreference = "Stop"

$deckDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$indexPath = Join-Path $deckDir "index.html"
$exportDir = Join-Path $deckDir "_ppt_export"
$slidesDir = Join-Path $exportDir "slides"
$chromeProfile = Join-Path $exportDir "chrome-profile"
$titlePrefix = -join @([char]0x6469, [char]0x767b, [char]0x8ff7, [char]0x57ce)
$pptxPath = Join-Path $deckDir ($titlePrefix + "_Gaze_in_shadows_pitch_deck.pptx")
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path -LiteralPath $chromePath)) {
  $chromePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}
if (-not (Test-Path -LiteralPath $chromePath)) {
  throw "No Chrome or Edge executable was found."
}

New-Item -ItemType Directory -Force -Path $exportDir, $slidesDir, $chromeProfile | Out-Null
Get-ChildItem -LiteralPath $slidesDir -File -ErrorAction SilentlyContinue | Remove-Item -Force

$html = Get-Content -LiteralPath $indexPath -Raw -Encoding UTF8
$style = [regex]::Match($html, "<style>(?<style>[\s\S]*?)</style>").Groups["style"].Value
$slides = [regex]::Matches($html, '<section class="slide[\s\S]*?</section>')
if ($slides.Count -eq 0) {
  throw "No slides found in index.html."
}

$baseUri = (New-Object System.Uri($deckDir + "\")).AbsoluteUri
$exportCss = @"
html, body {
  width: 1920px;
  height: 1080px;
  overflow: hidden;
}
body {
  margin: 0;
}
.deck {
  width: 100vw;
  height: 100vh;
  display: block;
  overflow: hidden;
}
.slide {
  width: 100vw;
  height: 100vh;
  flex: none;
}
.controls {
  display: none !important;
}
"@

$pngPaths = @()
for ($i = 0; $i -lt $slides.Count; $i++) {
  $num = ($i + 1).ToString("00")
  $slideHtmlPath = Join-Path $slidesDir "slide_$num.html"
  $slidePngPath = Join-Path $slidesDir "slide_$num.png"
  $slideDoc = @"
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="$baseUri">
  <style>
$style
$exportCss
  </style>
</head>
<body>
  <main class="deck">
$($slides[$i].Value)
  </main>
</body>
</html>
"@
  Set-Content -LiteralPath $slideHtmlPath -Value $slideDoc -Encoding UTF8
  $slideUri = (New-Object System.Uri($slideHtmlPath)).AbsoluteUri
  & $chromePath `
    --headless=new `
    --disable-gpu `
    --hide-scrollbars `
    --allow-file-access-from-files `
    --run-all-compositor-stages-before-draw `
    --virtual-time-budget=2200 `
    --force-device-scale-factor=1 `
    --user-data-dir="$chromeProfile" `
    --window-size=1920,1080 `
    --screenshot="$slidePngPath" `
    "$slideUri" | Out-Null
  if (-not (Test-Path -LiteralPath $slidePngPath)) {
    throw "Failed to export screenshot: $slidePngPath"
  }
  $pngPaths += $slidePngPath
}

if (Test-Path -LiteralPath $pptxPath) {
  Remove-Item -LiteralPath $pptxPath -Force
}

$powerPoint = New-Object -ComObject PowerPoint.Application
$presentation = $powerPoint.Presentations.Add()
$presentation.PageSetup.SlideWidth = 960
$presentation.PageSetup.SlideHeight = 540
$blankLayout = 12

foreach ($png in $pngPaths) {
  $slide = $presentation.Slides.Add($presentation.Slides.Count + 1, $blankLayout)
  $shape = $slide.Shapes.AddPicture($png, $false, $true, 0, 0, 960, 540)
}

$presentation.SaveAs($pptxPath)
$presentation.Close()
$powerPoint.Quit()

[PSCustomObject]@{
  Slides = $pngPaths.Count
  Pptx = $pptxPath
  ExportDir = $slidesDir
}
