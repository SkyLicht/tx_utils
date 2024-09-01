import json
import numbers
from datetime import datetime
from enum import Enum
from typing import Optional

from numpy.ma.core import count, empty
from pydantic import BaseModel

from utils.file_management import timestamp_to_datetime
class Shifts(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

    def __str__(self):
        return self.name


class AndonBaseModel(BaseModel):
    downtime: str | None
    alert_min: float
    alerts_areas_name: str | None
    alerts_categories_name: str | None
    alerts_location: str | None
    alerts_reason: str | None
    alerts_start_date: str
    alerts_start_shift: str
    alerts_status_name: str | None
    alerts_id: int
    alerts_owners_name: Optional[str]
    employees_id: int
    finish: str
    first: str
    id: int
    level_1: str | None
    level_2: str | None
    message: str | None
    real_downtime: float
    start: str
    station: str | None
    total_min: float

    def __str__(self):
        return (
            f"Alert ID: {self.alerts_id},"
            f"ID: {self.id},"
            f"Shift: {self.alerts_start_shift},"
            f"Date: {self.alerts_start_date},"
            f"Start: {self.start},"
            f"Finish: {self.finish},"
            f"Total Min: {self.total_min},"
            f"First: {self.first},"
            f"Area: {self.alerts_areas_name},"
            f"Location: {self.alerts_location},"
            f"Category: {self.alerts_categories_name},"
            f"Reason: {self.alerts_reason},"
            f"Status: {self.alerts_status_name},"
            f"Owners: {self.alerts_owners_name},"
            f"Employee ID: {self.employees_id},"
            f"Level 1: {self.level_1},"
            f"Level 2: {self.level_2},"
            f"Message: {self.message},"
            f"Real Downtime: {self.real_downtime},"
            f"Station: {self.station},"
        )

class AndonByShiftModel(BaseModel):
    fist_shift: dict[str, list[AndonBaseModel]]
    second_shift: dict[str, list[AndonBaseModel]]
    third_shift: dict[str, list[AndonBaseModel]]

    def summary(self):
        first_shift_summary_equipment: dict[str, dict] = {}
        first_shift_summary_automation: dict[str, dict] = {}
        for key, value in self.fist_shift.items():
            # for a in value:
            #     if a.owners_name == "G2 Equipment":
            #         print(a.owners_name, a.alerts_areas_name, a.total_min)
            first_shift_summary_equipment[key] = {
                "Total": count([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
                "Downtime": sum([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
                "Minutes": sum([_record.total_min for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
            }

            first_shift_summary_automation[key] = {
                "Total": count([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Automation"]),
                "Downtime": sum([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Automation"]),
                "Minutes": sum([_record.total_min for _record in value if _record.alerts_owners_name == "G2 Automation"]),
            }

        second_shift_summary_equipment: dict[str, dict] = {}
        second_shift_summary_automation: dict[str, dict] = {}

        for key, value in self.second_shift.items():
            second_shift_summary_equipment[key] = {
                "Total": count([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
                "Downtime": sum([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
                "Minutes": sum([_record.total_min for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
            }

            second_shift_summary_automation[key] = {
                "Total": count([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Automation"]),
                "Downtime": sum([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Automation"]),
                "Minutes": sum([_record.total_min for _record in value if _record.alerts_owners_name == "G2 Automation"]),
            }

        third_shift_summary_equipment: dict[str, dict] = {}
        third_shift_summary_automation: dict[str, dict] = {}

        for key, value in self.third_shift.items():
            third_shift_summary_equipment[key] = {
                "Total": count([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
                "Downtime": sum([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
                "Minutes": sum([_record.total_min for _record in value if _record.alerts_owners_name == "G2 Equipment"]),
            }

            third_shift_summary_automation[key] = {
                "Total": count([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Automation"]),
                "Downtime": sum([_record.real_downtime for _record in value if _record.alerts_owners_name == "G2 Automation"]),
                "Minutes": sum([_record.total_min for _record in value if _record.alerts_owners_name == "G2 Automation"]),
            }

        return {
            "first": {
                "Equipment": first_shift_summary_equipment,
                "Automation": first_shift_summary_automation
            },
            "second": {
                "Equipment": second_shift_summary_equipment,
                "Automation": second_shift_summary_automation
            },
            "third": {
                "Equipment": third_shift_summary_equipment,
                "Automation": third_shift_summary_automation
            }
        }

class AndonGroupsModel(BaseModel):
    area_frontend: AndonByShiftModel
    area_backend: AndonByShiftModel

    def summary(self)-> dict[str, dict]:
        return {
            "Frontend": self.area_frontend.summary(),
            "Backend": self.area_backend.summary()
        }

    def to_list(self)-> list[dict]:
        _excel_data = []

        for key, value in self.summary().items():
            for shift, shift_data in value.items():
                for owner, owner_data in shift_data.items():
                    for location, location_data in owner_data.items():
                        _excel_data.append({
                            "Area": key,
                            "Shift": shift,
                            "Location": location,
                            "Owner": owner,
                            "Total": location_data["Total"],
                            "Downtime": location_data["Downtime"],
                            "Minutes": location_data["Minutes"]
                        })

        _filtered = [empty_line for empty_line in _excel_data if empty_line["Total"] > 0]


        return _filtered





    def show(self):
        print("Frontend")
        print("First Shift")
        for key, value in self.area_frontend.fist_shift.items():
            print(f"Location: { 
                key
            }")
            for _record in value:
                print(_record)
        print("Second Shift")
        for key, value in self.area_frontend.second_shift.items():
            print(f"Location: { 
                key
            }")
            for _record in value:
                print(_record)
        print("Third Shift")
        for key, value in self.area_frontend.third_shift.items():
            print(f"Location: { 
                key
            }")
            for _record in value:
                print(_record)
        print("Backend")
        print("First Shift")
        for key, value in self.area_backend.fist_shift.items():
            print(f"Location: { 
                key
            }")
            for _record in value:
                print(_record)
        print("Second Shift")
        for key, value in self.area_backend.second_shift.items():
            print(f"Location: { 
                key
            }")
            for _record in value:
                print(_record)
        print("Third Shift")
        for key, value in self.area_backend.third_shift.items():
            print(f"Location: { 
                key
            }")
            for _record in value:
                print(_record)




def translate_var_name(data: list[dict]) -> list[AndonBaseModel]:
    _models: list[AndonBaseModel] = []
    for _record in data:
        _model = AndonBaseModel(
            downtime=_record['PRD_DT'],
            alert_min=is_not_float(_record['alert_mins']),
            alerts_areas_name=_record['alerts__areas__name'],
            alerts_categories_name=_record['alerts__categories__name'],
            alerts_location=_record['alerts__location'],
            alerts_reason=_record['alerts__reason'],
            alerts_start_date=timestamp_to_datetime(_record['alerts__start__date']).isoformat(),
            alerts_start_shift=Shifts(_record['alerts__start__shift']),
            alerts_status_name=_record['alerts__status__name'],
            alerts_id=_record['alerts_id'],
            alerts_owners_name=_record['alerts_owners__name'],
            employees_id=_record['employees_id'],
            finish=timestamp_to_datetime(_record['finish']).isoformat()
                if isinstance(_record["finish"], numbers.Number)
                else timestamp_to_datetime(_record['alerts__start__date']).isoformat(),
            first=timestamp_to_datetime(_record['first']).isoformat()
                if isinstance(_record["first"], numbers.Number)
                else timestamp_to_datetime(_record['alerts__start__date']).isoformat(),
            id=_record['id'],
            level_1=_record['level_1'],
            level_2=_record['level_2'],
            message=str(_record['message']),
            real_downtime=_record['real_downtime'],
            start=timestamp_to_datetime(_record['start']).isoformat()
                if isinstance(_record["start"], numbers.Number)
                else timestamp_to_datetime(_record['alerts__start__date']).isoformat(),
            station=_record['station'],
            total_min=_record['total_mins']
        )
        _models.append(_model)

    return _models

def is_not_float(s: str) -> float:
    try:
        return float(s)
    except ValueError:
        return 0.0
    except TypeError:
        return 0.0
    except Exception as e:
        print(e)
        return 0.0

def group_by_alerts_id(data: list[AndonBaseModel]) -> dict[int, list[AndonBaseModel]]:
    _refined: dict[int, list[AndonBaseModel]] = {}
    for _record in data:
        if _record.alerts_id in _refined:
            _refined[_record.alerts_id].append(_record)
        else:
            _refined[_record.alerts_id] = [_record]
    return _refined


def group_by(filtered, param):
    _refined: dict[str, list[AndonBaseModel]] = {}
    for _record in filtered:
        if getattr(_record, param) in _refined:
            _refined[getattr(_record, param)].append(_record)
        else:
            _refined[getattr(_record, param)] = [_record]
    return _refined




def get_refined_andons(data: list[dict])-> AndonGroupsModel:
    _refined = group_by_alerts_id(translate_var_name(data))

    filter_by_employee: list[AndonBaseModel] = [
        _record
        for value in _refined.values()
        for _record in value
        if _record.employees_id > 0
    ]


    # deleted Alert Id's duplicated
    # Assuming AndonBaseModel has a unique 'alerts_id' attribute
    # filter_by_min_unique = list({record.alerts_id: record for record in filter_by_downtime}.values())

    filter_by_frontend: list[AndonBaseModel] = [
        _record
        for _record in filter_by_employee
        if _record.alerts_areas_name == "G2 Frontend"
    ]
    filter_by_backend: list[AndonBaseModel] = [
        _record
        for _record in filter_by_employee
        if _record.alerts_areas_name == "G2 Backend"
    ]

    filter_frontend_by_shift: dict[str, list[AndonBaseModel]] = group_by(filter_by_frontend, "alerts_start_shift")
    filter_backend_by_shift: dict[str, list[AndonBaseModel]] = group_by(filter_by_backend, "alerts_start_shift")


    filter_frontend_first_by_location: dict[str, list[AndonBaseModel]] = (
        group_by(filter_frontend_by_shift.get("1"), "alerts_location"))
    filter_frontend_second_by_location: dict[str, list[AndonBaseModel]] = (
        group_by(filter_frontend_by_shift.get("2"), "alerts_location"))
    filter_frontend_third_by_location: dict[str, list[AndonBaseModel]] = (
        group_by(filter_frontend_by_shift.get("3"), "alerts_location"))

    filter_backend_first_by_location: dict[str, list[AndonBaseModel]] = (
        group_by(filter_backend_by_shift.get("1"), "alerts_location"))
    filter_backend_second_by_location: dict[str, list[AndonBaseModel]] = (
        group_by(filter_backend_by_shift.get("2"), "alerts_location"))
    filter_backend_third_by_location: dict[str, list[AndonBaseModel]] = (
        group_by(filter_backend_by_shift.get("3"), "alerts_location"))

    _area_frontend = AndonByShiftModel(
        fist_shift=filter_frontend_first_by_location,
        second_shift=filter_frontend_second_by_location,
        third_shift=filter_frontend_third_by_location
    )

    _area_backend = AndonByShiftModel(
        fist_shift=filter_backend_first_by_location,
        second_shift=filter_backend_second_by_location,
        third_shift=filter_backend_third_by_location
    )


    _andon_groups = AndonGroupsModel(
        area_frontend=_area_frontend,
        area_backend=_area_backend
    )

    return _andon_groups
