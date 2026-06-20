# BDHEI Calculator

Clean Python implementation of the Blended Drought and High-temperature Evapotranspiration Index (BDHEI).

This project is being prepared locally before any GitHub release. It has not been uploaded to a remote repository.

## Associated Paper

Huang, J., Li, X., Wang, L., Wang, X., Li, S., and Zhang, F. (2026). Construction and performance evaluation of a compound high-temperature and drought index for summer in Southwest China. *Natural Hazards*, 122, Article 475.

DOI: <https://doi.org/10.1007/s11069-026-08252-0>

## Method

For paired SPEI-3 and STI observations, the program:

1. estimates marginal cumulative probabilities with Gaussian KDE;
2. selects and fits a bivariate copula;
3. computes the BDHEI joint probability as `1 - F_STI(y) + C(F_SPEI(x), F_STI(y))`;
4. applies the standard normal quantile transformation.

The core BDHEI formula is kept consistent with the original research script. The public-facing output column is named `BDHEI`.

For details, see [docs/method.md](docs/method.md).

## Install

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
```

If you prefer to run directly from source without installing the package:

```powershell
$env:PYTHONPATH = "$PWD\src"
```

The dependency versions are pinned in [requirements.txt](requirements.txt) to support reproducible local verification.

## Quick Start With Example Data

The repository includes a tiny CSV example for checking the command-line workflow:

```powershell
bdhei compute `
  --spei-dir "examples\sample_spei" `
  --sti-dir "examples\sample_sti" `
  --output-dir "examples\output" `
  --spei-glob "*.csv" `
  --sti-suffix "_STI_M_03.csv" `
  --months 6 7 8
```

The same command is available as [configs/example_run.ps1](configs/example_run.ps1).

If `python` is not available on your command line, set `BDHEI_PYTHON` to your Python executable path before running the PowerShell scripts.

The example data are fully synthetic toy data created only to demonstrate file format and command-line usage. They do not represent any real weather station or observation record.

## Run With Your Own Data

```powershell
bdhei compute `
  --spei-dir "path\to\spei_files" `
  --sti-dir "path\to\sti_files" `
  --output-dir "path\to\output" `
  --months 6 7 8
```

For private research paths, copy [configs/research.template.ps1](configs/research.template.ps1) to a script under `local/` and edit the paths there. The `local/` directory is ignored by Git so machine-specific paths are not published.

## Input Format

Each SPEI file should contain:

- `date`
- `SPEI_3`

Each STI file should contain:

- `date`
- `STI`

Supported input file types are `.xlsx`, `.xls`, and `.csv`. The pinned environment includes `openpyxl` for `.xlsx` and `xlrd` for `.xls`.

By default, SPEI station IDs are read from filenames such as `SYNTHETIC_SITE_001_SPEI.csv`, and matching STI files are expected as `SYNTHETIC_SITE_001_STI_M_03.csv`.

## Example Data

A tiny CSV example is available under [examples](examples). It is only for checking input format and command-line behavior, not for scientific analysis.

## Output

For each station, the program writes an Excel workbook named like:

```text
SYNTHETIC_SITE_001_BDHEI_BestCopula.xlsx
```

The workbook contains:

- `BDHEI`: date, SPEI-3, STI, calculated BDHEI, selected copula type, selected copula parameters;
- `Copula_Compare`: candidate copula parameters and goodness-of-fit statistics.

The batch run also writes:

```text
Copula_scores_allstations.xlsx
```

## Verification Status

Current local checks:

- Public synthetic example run: passed.
- Release preflight check: passed.
- Local regression checks against private reference outputs: passed on the development machine. The private data and generated outputs are not included in this repository.

Run the directory comparison with:

```powershell
python tests\compare_directory_outputs.py `
  --reference-dir "path\to\legacy_reference_outputs" `
  --reference-pattern "{station_id}_legacy_reference.xlsx" `
  --reference-sheet "reference_sheet_name" `
  --reference-column "reference_column_name" `
  --new-dir "path\to\new_BDHEI_outputs" `
  --tolerance 0.001
```

For release-file checks before creating a public repository, see [docs/release.md](docs/release.md) and run:

```powershell
python tools\preflight_release.py
```

## Citation

Please cite the paper above when using this code. A machine-readable citation file is provided in [CITATION.cff](CITATION.cff).

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
