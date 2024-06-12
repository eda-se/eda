from typing import Literal, NamedTuple
import re

import pandas as pd
import numpy as np

ColumnType = Literal[
    "int64",
    "float64",
    "datetime64",
    "object",
    "category",
]
ColumnInfo = NamedTuple("ColumnInfo", [
    ("name", str),
    ("type", ColumnType),
])
column_info = (
    ColumnInfo(name="Integer", type="int64"),
    ColumnInfo(name="Float", type="float64"),
    ColumnInfo(name="Datetime", type="datetime64"),
    ColumnInfo(name="String", type="object"),
    ColumnInfo(name="Categorical", type="category"),
)

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


def is_numeric_type(column_type: str) -> bool:
    return column_type == column_info[0].type \
        or column_type == column_info[1].type


def is_date_type(column_type: str) -> bool:
    return column_type == column_info[2].type


def is_categorical_type(column_type: str) -> bool:
    return column_type == column_info[4].type \
        or column_type == column_info[3].type


def convert_dataframe_float_columns_to_int(df: pd.DataFrame) -> None:
    for name, values in df.items():
        if values.dtype == column_info[1].type and is_int_column(values):
            convert_column_data_type(df, name, "int64")


def convert_numeric_strings_to_numbers(df: pd.DataFrame) -> None:
    for name, values in df.items():
        if values.dtype == "object" or values.dtype == "float64":
            if is_int_column(values):
                convert_column_data_type(df, name, "int64")
            elif is_float_column(values):
                convert_column_data_type(df, name, "float64")


def convert_column_data_type(
    df: pd.DataFrame,
    column_name: str,
    column_type: ColumnType
) -> None:
    column = df[column_name]
    match column_type:
        case "object":
            df[column_name] = column.astype(str)
        case "int64":
            df[column_name] = np.floor(pd.to_numeric(column)) \
                .astype("Int64")
        case "float64":
            if column.dtype == "object":
                df[column_name] = pd.to_numeric(
                    errors="coerce"
                )
            else:
                df[column_name] = pd.to_numeric(column)
        case "datetime64":
            datetime_pattern = "%Y-%m-%dT%H:%M:%S"
            df[column_name] = pd.to_datetime(
                column,
                format=datetime_pattern
            )
        case "category":
            df[column_name] = column.astype("category")


def get_types_from_dataframe(df: pd.DataFrame) -> dict[str, str]:
    result: dict[str, str] = {}
    for column in df:
        column_type = df[column].dtype.name.lower()
        for cinfo in column_info:
            if column_type == cinfo.type:
                result[column] = cinfo.type
                break

        if column not in result:
            if column_info[2].type in column_type:
                result[column] = column_info[2].type
            else:
                result[column] = column_info[3].type

    return result
