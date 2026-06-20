# Example Data

This folder contains a tiny station-level CSV example for `SYNTHETIC_SITE_001`.

The data are fully synthetic toy values created only for checking input format and command-line behavior. They are not copied, sampled, perturbed, renamed, or derived from any real weather station observation. They are too small for scientific analysis. Use complete station records for research calculations.

Run:

```powershell
bdhei compute `
  --spei-dir "examples\sample_spei" `
  --sti-dir "examples\sample_sti" `
  --output-dir "examples\output" `
  --spei-glob "*.csv" `
  --sti-suffix "_STI_M_03.csv" `
  --months 6 7 8
```

From a source checkout without package installation, set `PYTHONPATH=src` and run `python -m bdhei.cli compute ...` with the same arguments.
