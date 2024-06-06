import base64
import csv
import io

import pandas as pd


def get_dataframe_from_contents(content: str) -> pd.DataFrame:
    content_type, content_string = content.split(',')
    if content_type.startswith('data:text/csv'):
        decoded = base64.b64decode(content_string).decode('utf-8')
        dialect = csv.Sniffer().sniff(decoded)
        df = pd.read_csv(io.StringIO(decoded), sep=dialect.delimiter)
        return df
    else:
        raise TypeError("Invalid content type")
