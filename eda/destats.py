import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr, skew
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from sklearn.cluster import KMeans

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


# 2D
def clean_columns(x, y):
    mask = ~np.isnan(x) & ~np.isnan(y) & ~np.isinf(x) & ~np.isinf(y)
    return x[mask], y[mask]

def pearson_correlation(x: pd.Series, y: pd.Series) -> float:
    return pearsonr(x, y)[0]

def spearman_correlation(x: pd.Series, y: pd.Series) -> float:
    return spearmanr(x, y)[0]

def coefficient_of_determination(x: pd.Series, y: pd.Series) -> float:
    x_reshaped = x.values.reshape(-1, 1)
    model = LinearRegression().fit(x_reshaped, y)
    return model.score(x_reshaped, y)

def linear_regression(x: pd.Series, y: pd.Series) -> str:
    x_reshaped = x.values.reshape(-1, 1)
    model = LinearRegression().fit(x_reshaped, y)
    intercept = model.intercept_
    slope = model.coef_[0]
    return f"""Intercept: {intercept}
Współczynnik nachylenia: {slope}
Równanie: y = {intercept} + {slope}x"""


def confidence_interval(x: pd.Series, y: pd.Series, alpha=0.05) -> str:
    x_with_const = sm.add_constant(x)
    model = sm.OLS(y, x_with_const).fit()
    conf = model.conf_int(alpha)
    return f"""Przedział ufności dla interceptu: {conf.loc["const"].tolist()}
Przedział ufności dla współczynnika nachylenia: {conf.loc[x.name].tolist()}"""


def correlation_coefficient(x: pd.Series, y: pd.Series) -> float:
    return x.corr(y)


def anova_analysis(data: pd.DataFrame, formula: str) -> dict:
    model = ols(formula, data).fit()
    anova_results = anova_lm(model)
    return {
        "Metoda": "ANOVA",
        "Wyniki": anova_results.to_dict()
    }


def ancova_analysis(data: pd.DataFrame, formula: str) -> dict:
    model = ols(formula, data).fit()
    anova_results = anova_lm(model, typ=2)
    return {
        "Metoda": "ANCOVA",
        "Wyniki": anova_results.to_dict()
    }


def cluster_analysis(data: pd.DataFrame, n_clusters: int) -> dict:
    model = KMeans(n_clusters=n_clusters)
    clusters = model.fit_predict(data)
    return {
        "Metoda": "Analiza skupień",
        "Wyniki": {
            "Klasyfikacja": clusters.tolist(),
        }
    }
