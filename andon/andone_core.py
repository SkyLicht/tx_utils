import json

import pandas as pd
from icecream import ic

from andon.andon_models import get_refined_andons
from prouction_data.hph_data_from_db import get_line_status_model_data
from utils.file_management_util import su_read_excel_file


def main():
    production_data = get_line_status_model_data()
    data = su_read_excel_file("../files/andons/in/andon_2024-08-28.xlsx")


    _list_data = get_refined_andons(data).to_list()
    _andon_report = []

    # ic(_list_data)

    # ic(production_data.get('smt'))
    # ic(production_data.get('packing'))

    # for _record in _list_data:
    #     if _record['Area'] == "Frontend" and _record['Owner'] == "Equipment":
    #         if _record["Shift"] == "First Shift":
    #             for e in production_data.get('smt') :
    #                 if e.line == _record['Location'] and e.shift == "first":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #         if _record["Shift"] == "Second Shift":
    #             for e in production_data.get('smt') :
    #                 if e.line == _record['Location'] and e.shift == "second":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #         if _record["Shift"] == "Third Shift":
    #             for e in production_data.get('smt') :
    #                 if e.line == _record['Location'] and e.shift == "third":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #
    #     if _record['Area'] == "Frontend" and _record['Owner'] == "Automation":
    #         if _record["Shift"] == "First Shift":
    #             for e in production_data.get('smt') :
    #                 if e.line == _record['Location'] and e.shift == "first":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #         if _record["Shift"] == "Second Shift":
    #             for e in production_data.get('smt') :
    #                 if e.line == _record['Location'] and e.shift == "second":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #         if _record["Shift"] == "Third Shift":
    #             for e in production_data.get('smt') :
    #                 if e.line == _record['Location'] and e.shift == "third":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #
    #     if _record['Area'] == "Backend" and _record['Owner'] == "Equipment":
    #         if _record["Shift"] == "First Shift":
    #             for e in production_data.get('packing') :
    #                 if e.line == _record['Location'] and e.shift == "first":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #         if _record["Shift"] == "Second Shift":
    #             for e in production_data.get('packing') :
    #                 if e.line == _record['Location'] and e.shift == "second":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #         if _record["Shift"] == "Third Shift":
    #             for e in production_data.get('packing') :
    #                 if e.line == _record['Location'] and e.shift == "third":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #
    #     if _record['Area'] == "Backend" and _record['Owner'] == "Automation":
    #         if _record["Shift"] == "First Shift":
    #             for e in production_data.get('packing') :
    #                 if e.line == _record['Location'] and e.shift == "first":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #         if _record["Shift"] == "Second Shift":
    #             for e in production_data.get('packing') :
    #                 if e.line == _record['Location'] and e.shift == "second":
    #                     _andon_report.append({**_record, **e.dict()})
    #
    #         if _record["Shift"] == "Third Shift":
    #             for e in production_data.get('packing') :
    #                 if e.line == _record['Location'] and e.shift == "third":
    #                     _andon_report.append({**_record, **e.dict()})




    # df = pd.DataFrame(_andon_report)
    # df.drop(['Shift', "Location"], axis=1, inplace=True)

    # Save to Excel
    # df.to_excel("../files/andons/out/andon_report.xlsx", index=False)
    #
    #
    # ic(df)


    # Equipment

    def search_for_andon_(area=None, location=None, owner=None, shift=None):
        for record in _list_data:
            if area and record['Area'] != area:
                continue
            if location and record['Location'] != location:
                continue
            if owner and record['Owner'] != owner:
                continue
            if shift and record['Shift'] != shift:
                continue
            # Return the first matching record
            return record
        # If no record matches, return None
        return None

    def search_for_andon_list(location=None, owner=None, shift=None):
        filtered_records = []

        for record in _list_data:
            if location and record['Location'] != location:
                continue
            if owner and record['Owner'] != owner:
                continue
            if shift and record['Shift'] != shift:
                continue

            filtered_records.append(record)

        return filtered_records


    for smt in production_data.get('smt'):
        sa = search_for_andon_(area="Frontend", location=smt.line, owner="Equipment", shift=smt.shift)
        _record_ee = {
            "area": "smt",
            "owner": "Equipment",
            "total": 0 if sa is None else sa['Total'],
            "down_time": 0 if sa is None else sa['Downtime'],
            "line": smt.line,
            "shift": smt.shift,
            "output": smt.output,
            "commit": smt.commit,
            "gap": smt.lost_units,
            "lost_time": smt.lost_time,
        }

        _andon_report.append(_record_ee)



    for packing in production_data.get('packing'):
        sa = search_for_andon_(area="Backend", location=packing.line, owner="Equipment", shift=packing.shift)
        _record_ee = {
            "area": "packing",
            "owner": "Equipment",
            "total": 0 if sa is None else sa['Total'],
            "down_time": 0 if sa is None else sa['Downtime'],
            "line": packing.line,
            "shift": packing.shift,
            "output": packing.output,
            "commit": packing.commit,
            "gap": packing.lost_units,
            "lost_time": packing.lost_time,
        }

        _andon_report.append(_record_ee)

        sa_l = search_for_andon_list(location=packing.line, owner="Automation", shift=packing.shift)
        _record_ea = {
            "area": "packing",
            "owner": "Automation",
            "total": sum([a['Total'] for a in sa_l]),
            "down_time": sum([a['Downtime'] for a in sa_l]),
            "line": packing.line,
            "shift": packing.shift,
            "output": packing.output,
            "commit": packing.commit,
            "gap": packing.lost_units,
            "lost_time": packing.lost_time,
        }

        _andon_report.append(_record_ea)

    for p in _andon_report:
        print(p)


    df = pd.DataFrame(_andon_report)

    # Save to Excel
    df.to_excel("../files/andons/out/andon_report_2024-08-29.xlsx", index=False)







    # for p in _andon_report :
    #     print(p)

if __name__ == "__main__":
    main()