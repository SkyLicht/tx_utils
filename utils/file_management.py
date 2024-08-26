import json
from datetime import datetime, timedelta, timezone

import pandas as pd
from icecream import ic


# Read Excel file using pandas
def su_read_excel_file(
        file_path: str,
        sheet_name: str = None,
        validate_column: list[str] = None,
        drop_row: int = 1
)-> list[dict]| None:
    """
    Read Excel file using pandas
    :param validate_column:
    :param sheet_name:
    :param file_path: str: path to the file
    """
    try:
        df = pd.read_excel(file_path) if sheet_name is None else pd.read_excel(file_path, sheet_name=sheet_name)
        if validate_column:
            for column in validate_column:
                if column not in df.columns:
                    raise Exception(f"Column {column} not found in the file")

        # Drop last row
        if drop_row > 0:
            df = df[:-drop_row]
        _result = su_df_to_json(df, show=False)
        return _result
    except Exception as e:
        print(e)
        return None


def su_df_to_json(df: pd.DataFrame, show: bool = True):
    resul = df.to_json(orient="records")
    parsed = json.loads(resul)
    if show:
        ic(parsed)
    return parsed


def excel_serial_to_datetime(excel_serial: int) -> datetime:
    # Excel's base date is January 1, 1900, but Excel incorrectly treats 1900 as a leap year
    base_date = datetime(1899, 12, 30)  # Adjust base date due to Excel's leap year bug
    delta = timedelta(days=excel_serial)
    return base_date + delta

# Function to convert milliseconds to a human-readable datetime
def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000.0 , tz=timezone.utc)
