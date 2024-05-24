import pandas as pd
import re

__NUMBER_REGEX = re.compile(r"^\d+([,\.]\d+)?$")
__INT_REGEX = re.compile(r"^\d+([,\.]0)?$")
__FLOAT_REGEX = re.compile(r"^\d+[,\.]\d+$")


def __is_number(value: any) -> bool:
    if pd.isna(value):
        return True
    return bool(__NUMBER_REGEX.match(str(value)))


def __is_int(value: any) -> bool:
    if pd.isna(value):
        return True
    return bool(__INT_REGEX.match(str(value)))


def __is_float(value: any) -> bool:
    if pd.isna(value):
        return True
    return bool(__FLOAT_REGEX.match(str(value)))


def is_int_column(column: pd.Series) -> bool:
    return column.apply(__is_int).all()


def is_float_column(column: pd.Series) -> bool:
    if not column.apply(__is_number).all():
        return False
    return column.apply(__is_float).any()


def convert_column_data_type(df, col, dtype):
    if dtype == "object":
        df[col] = df[col].astype(str)
    elif dtype == "int64":
        df[col] = pd.to_numeric(
                df[col],
                downcast="integer",
                errors="raise") \
            .astype("Int64")
    elif dtype == "float64":
        if df[col].dtype == "object":
            df[col] = pd.to_numeric(
                df[col].str.replace(",", "."),
                errors="coerce"
            )
        else:
            df[col] = pd.to_numeric(df[col])
    elif dtype == "datetime64":
        datetime_pattern = "%Y-%m-%dT%H:%M:%S"
        df[col] = pd.to_datetime(
            df[col],
            errors="raise",
            format=datetime_pattern
        )
    elif dtype == "category":
        df[col] = df[col].astype("category")
