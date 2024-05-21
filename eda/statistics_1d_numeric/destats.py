import numpy as np
import pandas as pd


def unique_1d(values: pd.Series) -> np.ndarray:
    return values.unique()


def count_1d(values: pd.Series) -> pd.Series:
    return values.value_counts()


def proportion_1d(values: pd.Series) -> pd.Series:
    return values.value_counts() / values.count()


def mode_1d(values: pd.Series) -> pd.Series:
    return values.mode()


def na_count_1d(values: pd.Series) -> int:
    return values.isna().sum()


def median_1d(values: pd.Series) -> float:
    return values.median()


def mean_1d(values: pd.Series) -> float:
    return values.mean()


def std_deviation_1d(values: pd.Series) -> float:
    return values.std()


def variance_1d(values: pd.Series) -> float:
    return values.var()


def quantiles_1d(values: pd.Series, q: list[float]) -> pd.Series:
    return values.quantile(q)


def range_1d(values: pd.Series) -> float:
    return values.max() - values.min()


def skewness_1d(values: pd.Series) -> float:
    return values.skew()
