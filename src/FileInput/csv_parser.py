import base64
import io

import pandas as pd


def get_dataframe_from_contents(contents) -> pd.DataFrame | str:
    content_type, content_string = contents.split(',')
    if content_type.startswith('data:text/csv'):
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=";")
        return df
    else:
        return "Invalid content type"
