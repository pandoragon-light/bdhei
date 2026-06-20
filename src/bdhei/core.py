from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from copulas.bivariate import select_copula
from copulas.univariate import GaussianKDE
from scipy.stats import norm


@dataclass(frozen=True)
class BDHEIResult:
    """Calculated BDHEI values and fitted copula metadata."""

    data: pd.DataFrame
    copula_type: str
    copula_params: dict[str, Any]


def _fit_kde_cdf(values: pd.Series, eps: float) -> np.ndarray:
    kde = GaussianKDE()
    kde.fit(values.to_numpy())
    cdf = kde.cdf(values.to_numpy())
    return np.clip(cdf, eps, 1 - eps)


def _to_builtin(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _to_builtin(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_builtin(item) for item in value]
    return value


def calculate_bdhei(
    data: pd.DataFrame,
    drought_col: str = "SPEI_3",
    heat_col: str = "STI",
    output_col: str = "BDHEI",
    eps: float = 1e-6,
    ppf_clip: tuple[float, float] = (0.0001, 0.9999),
) -> BDHEIResult:
    """Calculate BDHEI from paired drought and heat index values.

    The probability formula follows the published BDHEI construction:
    P = 1 - F_heat(y) + C(F_drought(x), F_heat(y)).
    """

    missing = [col for col in (drought_col, heat_col) if col not in data.columns]
    if missing:
        raise KeyError(f"Missing required column(s): {', '.join(missing)}")

    work = data.copy()
    work = work.dropna(subset=[drought_col, heat_col]).reset_index(drop=True)
    if work.empty:
        raise ValueError("No valid paired observations after dropping missing values.")

    drought_cdf = _fit_kde_cdf(work[drought_col], eps=eps)
    heat_cdf = _fit_kde_cdf(work[heat_col], eps=eps)
    x = np.column_stack((drought_cdf, heat_cdf))

    best_copula = select_copula(x)
    best_copula.fit(x)

    joint_cdf = best_copula.cumulative_distribution(x)
    joint_prob = 1 - heat_cdf + joint_cdf

    work[output_col] = norm.ppf(np.clip(joint_prob, *ppf_clip))
    copula_type = type(best_copula).__name__
    copula_params = _to_builtin(best_copula.to_dict())
    work["Copula_Type"] = copula_type
    work["Copula_Params"] = str(copula_params)

    return BDHEIResult(
        data=work,
        copula_type=copula_type,
        copula_params=copula_params,
    )
