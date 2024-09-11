from datetime import datetime

import pandas as pd

from andon.andon_translate import translate_andon_data
from utils.file_management_util import su_read_excel_file, su_dict_group_by, convert_epoch_to_date, update_dict_in_list, \
    add_key_dict_in_list


def read_andon_file(path: str) -> list[dict]:
    _data = su_read_excel_file("../files/andons/in/andon_2024-08-27.xlsx")
    if not _data:
        return []
    # Group and clean data
    _group_by_id = su_dict_group_by(translate_andon_data(_data), "alerts_id")
    _collected = collect_data(_group_by_id, lambda x: x["employee_id"] > 0)
    _grouped_by = grouped_data_using_df(_collected, ["area_name", "location", "owners_name", "shift"])
    _filtered = list(
        filter(
            lambda x: x["owners_name"] == "Automation" or x["owners_name"] == "Equipment",
            _grouped_by
        )
    )
    return _filtered

# Make another func to collect data where the filter is the finish date
def collect_data(data: dict[str, list[dict]], lambda_func)-> list[dict]:
    # Collect data that meet the condition
    # If there are more than one record, append the one with the greater finish date
    _return = []
    for key, value in data.items():
        _collected = []
        for v in value:
            if lambda_func(v):
                _collected.append(v)

        if len(_collected) > 1:
           # append of the finish date is greater than the other finish date
           _greater_date = _collected[0]
           for e in _collected:
               if e['finish'] > _greater_date['finish']:
                   _greater_date = e
           _collected.append(_greater_date)
        elif len(_collected) == 1:
            _return.append(_collected[0])


    return _return

def grouped_data_using_df(data: list[dict], args: list[str])-> list[dict]:
    df = pd.DataFrame(data)

    df['date'] = df['date'].apply(convert_epoch_to_date)
    df['start'] = df['start'].apply(convert_epoch_to_date)
    df['first'] = df['first'].apply(convert_epoch_to_date)
    df['finish'] = df['finish'].apply(convert_epoch_to_date)

    grouped_df = df.groupby(args).agg({
        'alert_min': 'sum',  # Sum the alert minutes in each group
        'downtime': 'sum',  # Sum the downtime in each group
        'total_alerts': 'sum',  # Sum the total alerts in each group
    }).reset_index()

    return grouped_df.to_dict(orient="records")


def report(path: str)-> list[dict]:

    _data = su_read_excel_file(path)
    if not _data:
        return []

    # Group and clean data
    _group_by_id = su_dict_group_by(translate_andon_data(_data), "alerts_id")


    _collected = collect_data(_group_by_id, lambda x: x["employee_id"] > 0)

    update_dict_in_list(
        data= _collected,
        key= "date",
        lambda_func= lambda x: convert_epoch_to_date(_epoch_time= x, _format='%Y-%m-%d')
    )


    add_key_dict_in_list(
        data= _collected,
        new_key= "week",
        lambda_func= lambda x: datetime.strptime(x['date'], '%Y-%m-%d').isocalendar()[1]
    )


    update_dict_in_list(
        data= _collected,
        key= "start",
        lambda_func= lambda x: convert_epoch_to_date(_epoch_time= x, _format='%Y-%m-%d %H:%M:%S')
    )

    update_dict_in_list(
        data= _collected,
        key= "first",
        lambda_func= lambda x: convert_epoch_to_date(_epoch_time= x, _format='%Y-%m-%d %H:%M:%S')
    )

    update_dict_in_list(
        data= _collected,
        key= "finish",
        lambda_func= lambda x: convert_epoch_to_date(_epoch_time= x, _format='%Y-%m-%d %H:%M:%S')
    )

    _grouped_by_date = su_dict_group_by(_collected, "date")


    _return_list = [_r for _r in _grouped_by_date.values()]

    for _record in _grouped_by_date.values():
        for r in _record:
            print(r)
        # filter_by_fuzion = list(
        #     filter(
        #         lambda x: x.get("level_2") == "Fuzion" or x.get("level_2") == "Fuzion DIMM",
        #         _record
        #     )
        # )
        # for r in filter_by_fuzion:
        #     print(r)
    # for _record in _grouped_by_date.values():
    #     for r in _record:
    #         #print(r)
    #         _return_list.append(r)
        # filter_by_fuzion = list(
        #     filter(
        #         lambda x: x.get("level_2") == "Fuzion" or x.get("level_2") == "Fuzion DIMM",
        #         _record
        #     )
        # )
        # for r in filter_by_fuzion:
        #     print(r)
    #Save to excel
    # df = pd.DataFrame(_return_list)
    # df.to_excel("../files/andons/out/past_two_months.xlsx", index=False)


    return []


if __name__ == '__main__':

    _week_report = report("../files/andons/in/report/andon_2024-07-to-2024-08.xlsx")
    # _data = read_andon_file("../files/andons/in/andon_2024-08-27.xlsx")
    # for d in _data:
    #     print(d)


