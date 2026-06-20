$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = if ($env:BDHEI_PYTHON) { $env:BDHEI_PYTHON } else { "python" }

$env:PYTHONPATH = "$projectRoot\.deps;$projectRoot\src"

& $python -m bdhei.cli compute `
  --spei-dir "$projectRoot\examples\sample_spei" `
  --sti-dir "$projectRoot\examples\sample_sti" `
  --output-dir "$projectRoot\examples\output" `
  --spei-glob "*.csv" `
  --sti-suffix "_STI_M_03.csv" `
  --months 6 7 8
