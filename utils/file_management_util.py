import json
import os
import re
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
    :param drop_row:
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

def su_dict_to_df(data: list[dict], show: bool = True) -> pd.DataFrame:
    df = pd.DataFrame(data)
    if show:
        ic(df)
    return df
def su_dict_to_excel(
        data: list[dict],
        file_name: str,
        file_path: str,
        sheet_name: str = 'Sheet1', show: bool = True
):
    df = su_dict_to_df(data, show=False)
    df.to_excel(f'{file_path}/{file_name}.xlsx', sheet_name=sheet_name, index=False)
    if show:
        ic(df)
    return df

def su_dict_to_json(data: list[dict], show: bool = True):
    resul = json.dumps(data)
    parsed = json.loads(resul)
    if show:
        ic(parsed)
    return parsed

def su_save_json_file(data: list[dict], file_name: str, file_path: str, show: bool = True):
    with open(f"{file_path}/{file_name}.json", "w") as f:
        json.dump(data, f)
    if show:
        ic(data)
def su_df_to_json(df: pd.DataFrame, show: bool = True):
    resul = df.to_json(orient="records")
    parsed = json.loads(resul)
    if show:
        ic(parsed)
    return parsed

def su_dict_group_by(data, param):
    """ Group data by a parameter """
    grouped: dict[str, list] = {}
    for _record in data:
        if _record.get(param)in grouped:
            grouped[_record.get(param)].append(_record)
        else:
            grouped[_record.get(param)] = [_record]
    return grouped



def excel_serial_to_datetime(excel_serial: int) -> datetime:
    # Excel's base date is January 1, 1900, but Excel incorrectly treats 1900 as a leap year
    base_date = datetime(1899, 12, 30)  # Adjust base date due to Excel's leap year bug
    delta = timedelta(days=excel_serial)
    return base_date + delta

# Function to convert milliseconds to a human-readable datetime
def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000.0 , tz=timezone.utc)

def convert_epoch_to_date(_epoch_time: int, _timezone: timezone = timezone.utc, _format: str = '%Y-%m-%d %H:%M:%S') -> str:
    return datetime.fromtimestamp(_epoch_time / 1000, tz=_timezone).strftime(_format)

def update_dict_in_list(data: list[dict], key: str,value: any = None, lambda_func = None) -> list[dict]:
    for record in data:
        if lambda_func:
            record[key] = lambda_func(record[key])
        else:
            record[key] = value
    return data

def add_key_dict_in_list(
        data: list[dict],
        new_key: str,
        lambda_func = None
) -> list[dict]:
    for record in data:
        if lambda_func:
            record.update({new_key: lambda_func(record)})

    return data


def su_read_name_of_files_from_path(dir_path: str) -> list[str]:
    """ Read the name of file from a path and list them
    :param dir_path: str: path to the directory
    """
    return [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

def su_extract_date_from_string(string: str, pattern: str) -> dict | None:
    """
    Extract date from a file name.

    :param string: str: name of the file
    :param pattern: str: regex pattern to extract the date
    :return: dict: date extracted from the file name (file_name, date) or None if no date matches
    """
    match = re.search(pattern, string)
    if match:
        date_str = match.group(0)
        try:
            # Attempt to parse the date based on the matched string format.
            return {
                "text": string,
                "date_str": date_str
            }
        except ValueError:
            return None
    return None

def su_read_file_line(path, line_number):
    try:
        with open(path, 'r', encoding='utf-16') as file:
            lines = file.readlines()
            if len(lines) >= line_number:
                return lines[line_number - 1].strip()
            else:
                return f"Line {line_number} does not exist in the file."
    except FileNotFoundError:
        return "File not found. Please check the path."



if __name__ == '__main__':

    pass






