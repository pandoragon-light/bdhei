# Copy this file to a script under local/ and edit the paths for your own computer.
# The local/ directory is ignored by Git so private machine paths are not published.

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = if ($env:BDHEI_PYTHON) { $env:BDHEI_PYTHON } else { "python" }

$env:PYTHONPATH = "$projectRoot\.deps;$projectRoot\src"

$speiDir = "path\to\your\SPEI-3-files"
$stiDir = "path\to\your\STI-files"
$outputDir = "$projectRoot\output\research-run"

& $python -m bdhei.cli compute `
  --spei-dir $speiDir `
  --sti-dir $stiDir `
  --output-dir $outputDir `
  --months 6 7 8
