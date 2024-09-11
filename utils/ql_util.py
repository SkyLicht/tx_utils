from datetime import datetime
from enum import Enum


def qa_print_list(data: list[str]):
    for _item in data:
         print(_item)

class DateFormat(Enum):
    DATE_FORMAT = 0
    SQL_FORMAT = 1

def qa_transform_str_date(str_date: str, _from: DateFormat, _to: DateFormat):
    _out: any = None

    if _from == DateFormat.DATE_FORMAT and _to == DateFormat.SQL_FORMAT:
        _format_date = str_date.split('/')
        _out = f"{_format_date[2]}-{_format_date[0]}-{_format_date[1]}"
    return _out


def qa_transform_str_time_subtract(s_time_1: str, s_time_2: str, _format:str = "%H:%M:%S")->int:
    return (datetime.strptime(s_time_2, _format) - datetime.strptime(s_time_1, _format)).seconds

def qa_transform_seconds_to(seconds: int, _type: int)-> float:
    # Type 0: Minutes
    # Type 1: Hours
    # Type 2: Days

    _out: float = 0.0
    if _type == 0:
        _out = seconds / 60
    elif _type == 1:
        _out = seconds / 3600
    elif _type == 2:
        _out = seconds / 86400

    return round(_out,2)