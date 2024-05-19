import pandas as pd


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
