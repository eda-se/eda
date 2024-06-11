import base64
from io import StringIO

import pandas as pd


class CSVParser:
    def __init__(self, column_separator=";", decimal_separator=",") -> None:
        self.column_separator = column_separator
        self.decimal_separator = decimal_separator

    def get_dataframe_from_contents(self, content: str) -> pd.DataFrame:
        content_type, content_string = content.split(",")
        if content_type.startswith("data:text/csv"):
            decoded = base64.b64decode(content_string).decode("utf-8")
            df = pd.read_csv(
                StringIO(decoded),
                sep=self.column_separator,
                decimal=self.decimal_separator,
                date_format="ISO8601"
            )
            df = pd.read_json(StringIO(df.to_json(date_format="iso")))
            return df
        else:
            raise TypeError("Invalid content type")
