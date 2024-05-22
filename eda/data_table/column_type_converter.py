import pandas as pd
import re

def convert_matching_column_to_float(df, column):
    pattern = re.compile(r'^\d+(,\d+)?$')
    
    def can_convert(x):
        if x is None:
            return True  # Skip None values
        return bool(pattern.match(str(x)))
    
    if df[column].apply(can_convert).all():
        df[column] = df[column].apply(lambda x: float(str(x).replace(',', '.')) if x is not None else None)
    return df

def convert_column_data_type(df, col, dtype):
    if dtype == 'object':
        df[col] = df[col].astype(str)
    elif dtype == 'int64':
        df[col] = pd.to_numeric(df[col], downcast='integer', errors='raise').astype('Int64')
    elif dtype == 'float64':
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')
        else: df[col] = pd.to_numeric(df[col], errors='raise')
    elif dtype == 'datetime64':
        datetime_pattern = "%Y-%m-%dT%H:%M:%S"
        df[col] = pd.to_datetime(df[col], errors='raise', format=datetime_pattern)
    elif dtype == 'category':
        df[col] = df[col].astype('category')
