from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from copulas.bivariate import Clayton, Frank, Gumbel
from scipy.stats import multivariate_normal, norm


def empirical_copula_c(x: np.ndarray, u: float, v: float) -> float:
    return float(np.mean((x[:, 0] <= u) & (x[:, 1] <= v)))


def gof_rmse_on_grid(x: np.ndarray, cdf_func: Callable[[float, float], float], m: int = 20) -> float:
    grid = np.linspace(1 / (m + 1), m / (m + 1), m)
    errors = []
    for uu in grid:
        for vv in grid:
            c_emp = empirical_copula_c(x, uu, vv)
            c_fit = float(cdf_func(uu, vv))
            errors.append((c_emp - c_fit) ** 2)
    return float(np.sqrt(np.mean(errors)))


def fit_gaussian_rho(x: np.ndarray) -> float:
    z1 = norm.ppf(x[:, 0])
    z2 = norm.ppf(x[:, 1])
    rho = np.corrcoef(z1, z2)[0, 1]
    return float(np.clip(rho, -0.99, 0.99))


def gauss_cdf_factory(rho: float) -> Callable[[float, float], float]:
    mvn = multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]])

    def _cdf(u: float, v: float) -> float:
        return float(mvn.cdf([norm.ppf(u), norm.ppf(v)]))

    return _cdf


def gauss_logpdf(u: np.ndarray, v: np.ndarray, rho: float) -> np.ndarray:
    z1 = norm.ppf(u)
    z2 = norm.ppf(v)
    logphi1 = -0.5 * z1**2 - 0.5 * np.log(2 * np.pi)
    logphi2 = -0.5 * z2**2 - 0.5 * np.log(2 * np.pi)

    one_minus = 1 - rho**2
    q = z1**2 - 2 * rho * z1 * z2 + z2**2
    logphi_rho = -np.log(2 * np.pi) - 0.5 * np.log(one_minus) - (q / (2 * one_minus))

    return logphi_rho - logphi1 - logphi2


def score_gaussian_copula(x: np.ndarray, grid_m: int = 20) -> dict[str, Any]:
    n = x.shape[0]
    k = 1
    rho = fit_gaussian_rho(x)

    logpdf = gauss_logpdf(x[:, 0], x[:, 1], rho)
    logpdf = np.where(np.isfinite(logpdf), logpdf, -1e12)
    loglik = float(np.sum(logpdf))

    return {
        "copula": "Gaussian",
        "dependence_param": rho,
        "kendall_tau": float(2 / np.pi * np.arcsin(rho)),
        "loglik": loglik,
        "AIC": float(2 * k - 2 * loglik),
        "BIC": float(k * np.log(n) - 2 * loglik),
        "GOF_RMSE_grid": gof_rmse_on_grid(x, gauss_cdf_factory(rho), m=grid_m),
    }


def score_archimedean(copula_cls: type, x: np.ndarray, grid_m: int = 20) -> dict[str, Any]:
    n = x.shape[0]
    k = 1
    copula = copula_cls()
    copula.fit(x)

    logpdf = copula.log_probability_density(x)
    logpdf = np.where(np.isfinite(logpdf), logpdf, -1e12)
    loglik = float(np.sum(logpdf))

    def cdf_func(u: float, v: float) -> float:
        value = copula.cumulative_distribution(np.array([[u, v]]))
        return float(np.asarray(value).ravel()[0])

    return {
        "copula": copula_cls.__name__,
        "dependence_param": getattr(copula, "theta", None),
        "kendall_tau": getattr(copula, "tau", None),
        "loglik": loglik,
        "AIC": float(2 * k - 2 * loglik),
        "BIC": float(k * np.log(n) - 2 * loglik),
        "GOF_RMSE_grid": gof_rmse_on_grid(x, cdf_func, m=grid_m),
    }


def score_candidate_copulas(
    x: np.ndarray,
    selected_copula_type: str,
    station_id: str,
    grid_m: int = 20,
) -> pd.DataFrame:
    import pandas as pd

    rows: list[dict[str, Any]] = []
    for cls in [Clayton, Frank, Gumbel]:
        try:
            row = score_archimedean(cls, x, grid_m=grid_m)
        except Exception as exc:
            row = {
                "copula": cls.__name__,
                "dependence_param": np.nan,
                "kendall_tau": np.nan,
                "loglik": np.nan,
                "AIC": np.nan,
                "BIC": np.nan,
                "GOF_RMSE_grid": np.nan,
                "error": str(exc),
            }
        rows.append(row)

    try:
        rows.append(score_gaussian_copula(x, grid_m=grid_m))
    except Exception as exc:
        rows.append(
            {
                "copula": "Gaussian",
                "dependence_param": np.nan,
                "kendall_tau": np.nan,
                "loglik": np.nan,
                "AIC": np.nan,
                "BIC": np.nan,
                "GOF_RMSE_grid": np.nan,
                "error": str(exc),
            }
        )

    score_df = pd.DataFrame(rows)
    score_df["station_id"] = station_id
    score_df["n"] = x.shape[0]
    score_df["selected_by_select_copula"] = (
        score_df["copula"].str.lower() == selected_copula_type.lower()
    ).astype(int)

    for criterion in ["AIC", "BIC"]:
        valid = score_df.dropna(subset=[criterion])
        if valid.empty:
            score_df[f"best_by_{criterion}"] = 0
        else:
            best_name = valid.loc[valid[criterion].idxmin(), "copula"]
            score_df[f"best_by_{criterion}"] = (score_df["copula"] == best_name).astype(int)

    return score_df
