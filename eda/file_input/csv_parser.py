import base64
import io

import pandas as pd


def get_dataframe_from_contents(content: str) -> pd.DataFrame:
    content_type, content_string = content.split(',')
    if content_type.startswith('data:text/csv'):
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=";")
        return df
    else:
        raise TypeError("Invalid content type")
