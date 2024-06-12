import numpy as np
import pandas as pd
from scipy.stats import zscore


def handle_outliers(df: pd.DataFrame, columns: list[str], find_method: str, fix_method: str) -> pd.DataFrame:
    for column in columns:
        try:
            outliers_index, lower_bound, upper_bound = find_outliers(df, column, find_method)
        except ValueError:
            return df
        df = fix_outliers(df, column, outliers_index, fix_method, lower_bound, upper_bound)
    return df


def find_outliers(df: pd.DataFrame, column: str, method: str) -> (pd.DataFrame, float, float):
    if method == "zscore":
        return find_outliers_zscore(df, column)
    elif method == "iqr":
        return find_outliers_iqr(df, column)
    else:
        raise ValueError("Method must be either 'zscore' or 'iqr'")


def find_outliers_zscore(df: pd.DataFrame, column: str) -> (pd.DataFrame, float, float):
    z_score = zscore(df[column])
    outliers_index = []
    for i in range(len(z_score)):
        if abs(z_score[i]) > 3:
            outliers_index.append(i)
    return outliers_index, -3, 3


def find_outliers_iqr(df: pd.DataFrame, column: str) -> (pd.DataFrame, float, float):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers_index = []
    for i in range(len(df[column])):
        if df[column][i] < lower_bound or df[column][i] > upper_bound:
            outliers_index.append(i)
    return outliers_index, lower_bound, upper_bound


def fix_outliers(
        df: pd.DataFrame, column: str, outliers_index: list, method: str, lower_bound: float, upper_bound: float
) -> (pd.DataFrame, float, float):
    if method == "remove":
        df = fix_outliers_remove(df, column, outliers_index)
    elif method == "cap":
        df = fix_outliers_cap(df, column, outliers_index, lower_bound, upper_bound)
    elif method == "mean":
        df = fix_outliers_mean(df, column, outliers_index)
    elif method == "median":
        df = fix_outliers_median(df, column, outliers_index)
    return df


def fix_outliers_remove(df: pd.DataFrame, column: str, outliers_index: list) -> pd.DataFrame:
    for index in outliers_index:
        df[column][index] = np.nan
    return df


def fix_outliers_cap(
        df: pd.DataFrame, column: str, outliers_index: list, lower_bound: float, upper_bound: float
) -> pd.DataFrame:
    for i in outliers_index:
        df[column][i] = lower_bound if df[column][i] < lower_bound else upper_bound
    return df


def fix_outliers_mean(df: pd.DataFrame, column: str, outliers_index: list) -> pd.DataFrame:
    mean_value = df[column].mean()
    for i in outliers_index:
        df[column][i] = mean_value
    return df


def fix_outliers_median(df: pd.DataFrame, column: str, outliers_index: list) -> pd.DataFrame:
    median_value = df[column].median()
    for i in outliers_index:
        df[column][i] = median_value
    return df
