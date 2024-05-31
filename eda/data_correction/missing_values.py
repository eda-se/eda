import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer


def handle_missing_values(df, column, strategy, missing_values="") -> pd.DataFrame:
    df[column] = df[column].replace([missing_values, None], np.nan)

    if strategy == "ffill":
        df[column] = df[column].ffill()
        return df
    else:
        try:
            imp = SimpleImputer(strategy=strategy)
            df[column] = pd.Series(imp.fit_transform(pd.DataFrame(df[column])).reshape(-1))
            return df
        except ValueError as e:
            print(e)
            return df
