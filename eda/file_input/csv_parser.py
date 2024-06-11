import base64
import csv
import io

import pandas as pd


class CSVParser:
    current_separator = ","

    @staticmethod
    def get_dataframe_from_contents(content: str) -> pd.DataFrame:
        content_type, content_string = content.split(',')
        if content_type.startswith('data:text/csv'):
            decoded = base64.b64decode(content_string).decode('utf-8')
            dialect = csv.Sniffer().sniff(decoded)
            CSVParser.current_separator = dialect.delimiter
            df = pd.read_csv(io.StringIO(decoded), sep=CSVParser.current_separator)
            return df
        else:
            raise TypeError("Invalid content type")
