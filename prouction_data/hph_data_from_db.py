import logging
from enum import Enum

import requests
from pydantic import BaseModel
# Set up logging to get detailed information if needed
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class HourDataModel(BaseModel):
    id: str
    hour: int
    smtIn: int
    smtOut: int
    packing: int


class HPHDataModel(BaseModel):
    id: str
    line: str
    planned_hours: float
    target_oee: float
    uph: int
    date: str
    week: int
    platform: str
    sku: str
    hours: list[HourDataModel]

    def __str__(self):
        return f"ID: {self.id}, Line: {self.line}, Planned Hours: {self.planned_hours}, Target OEE: {self.target_oee}, UPH: {self.uph}, Date: {self.date}, Week: {self.week}, Platform: {self.platform}, SKU: {self.sku}"


    @property
    def installed_uph(self):
        return round(self.uph * self.target_oee , 0)
    @property
    def unit_per_minutes(self):
        return (self.uph * self.target_oee) / 60

    @property
    def time_per_unit(self):
        return 1 / self.unit_per_minutes

    @property
    def commit_units(self):
        return round((self.uph * self.target_oee) * self.planned_hours, 0)

    @property
    def lost_time(self):
        if self.packing_total > self.commit_units:
            return 0
        return round(self.units_lost_packing * self.time_per_unit, 2)

    @property
    def units_lost_packing(self):
        return self.packing_total -  self.commit_units

    @property
    def packing_total(self):
        return sum([hour.packing for hour in self.hours])

    @property
    def third_shift_packing(self):
        return sum([hour.packing for hour in self.hours[:6]])

    @property
    def third_shift_output(self):
        return sum([hour.smtOut for hour in self.hours[:6]])

    @property
    def first_shift_packing(self):
        return sum([hour.packing for hour in self.hours[6:16]])
    @property
    def first_shift_output(self):
        return sum([hour.smtOut for hour in self.hours[6:16]])
    @property
    def second_shift_packing(self):
        return sum([hour.packing for hour in self.hours[16:]])
    @property
    def second_shift_output(self):
        return sum([hour.smtOut for hour in self.hours[16:]])

    @property
    def third_shift_commit(self):
        return int(round(self.installed_uph * 6.25 , 0 ))

    @property
    def first_shift_commit(self):
        return int(round(self.installed_uph * 9.25, 0))

    @property
    def second_shift_commit(self):
        return int(round(self.installed_uph * 7.75, 2))

class Shift(Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"

class LineStatusByShiftBaseModel(BaseModel):
    line: str
    shift: str
    output: int
    commit: int
    lost_units: int
    lost_time: float

    def __str__(self):
        return f" Shift: {self.shift}, Output: {self.output}, Commit: {self.commit}, Lost Units: {self.lost_units}, Lost Time: {self.lost_time}"

class LineStatusDataModel(BaseModel):
    hph_data_model: HPHDataModel
    date: str
    line: str
    planned_hours: float
    target_oee: float
    uph: int
    output: int
    commit: int
    lost_units: int
    lost_time: float

    @property
    def first_status(self):

        status_smt = LineStatusByShiftBaseModel(
            line = self.line,
            shift=Shift.FIRST,
            output= self.hph_data_model.first_shift_output,
            commit= self.hph_data_model.first_shift_commit,
            lost_units= self.hph_data_model.first_shift_output - self.hph_data_model.first_shift_commit,
            lost_time= round(
                (self.hph_data_model.first_shift_output - self.hph_data_model.first_shift_commit) * self.hph_data_model.time_per_unit , 2)
                if self.hph_data_model.first_shift_output - self.hph_data_model.first_shift_commit < 0
                else 0
            )

        status_packing = LineStatusByShiftBaseModel(
            line = self.line,
            shift=Shift.FIRST,
            output= self.hph_data_model.first_shift_packing,
            commit= self.hph_data_model.first_shift_commit,
            lost_units= self.hph_data_model.first_shift_packing - self.hph_data_model.first_shift_commit,
            lost_time= round(
                (self.hph_data_model.first_shift_packing - self.hph_data_model.first_shift_commit) * self.hph_data_model.time_per_unit , 2)
                if self.hph_data_model.first_shift_packing - self.hph_data_model.first_shift_commit < 0
                else 0
        )


        return  {
            "smt": status_smt,
            "packing": status_packing
        }

    @property
    def second_status(self):
        status_smt = LineStatusByShiftBaseModel(
            line = self.line,
            shift=Shift.SECOND,
            output=self.hph_data_model.second_shift_output,
            commit=self.hph_data_model.second_shift_commit,
            lost_units=self.hph_data_model.second_shift_output - self.hph_data_model.second_shift_commit,
            lost_time=  round(
                (self.hph_data_model.second_shift_output - self.hph_data_model.second_shift_commit) * self.hph_data_model.time_per_unit , 2)
                if self.hph_data_model.second_shift_output - self.hph_data_model.second_shift_commit < 0
                else 0
        )


        status_packing = LineStatusByShiftBaseModel(
            line = self.line,
            shift=Shift.SECOND,
            output= self.hph_data_model.second_shift_packing,
            commit= self.hph_data_model.second_shift_commit,
            lost_units= self.hph_data_model.second_shift_packing - self.hph_data_model.second_shift_commit,
            lost_time= round(
                (self.hph_data_model.second_shift_packing - self.hph_data_model.second_shift_commit) * self.hph_data_model.time_per_unit , 2)
                if self.hph_data_model.second_shift_packing - self.hph_data_model.second_shift_commit < 0
                else 0
        )

        return {
            "smt": status_smt,
            "packing": status_packing
        }


    @property
    def third_status(self):
        status_smt = LineStatusByShiftBaseModel(
            line = self.line,
            shift=Shift.THIRD,
            output=self.hph_data_model.third_shift_output,
            commit=self.hph_data_model.third_shift_commit,
            lost_units=self.hph_data_model.third_shift_output - self.hph_data_model.third_shift_commit,
            lost_time= round(
                (self.hph_data_model.third_shift_output - self.hph_data_model.third_shift_commit) * self.hph_data_model.time_per_unit , 2)
                if self.hph_data_model.third_shift_output - self.hph_data_model.third_shift_commit < 0
                else 0
        )
        status_packing = LineStatusByShiftBaseModel(
            line = self.line,
            shift=Shift.THIRD,
            output= self.hph_data_model.third_shift_packing,
            commit= self.hph_data_model.third_shift_commit,
            lost_units= self.hph_data_model.third_shift_packing - self.hph_data_model.third_shift_commit,
            lost_time= round(
                (self.hph_data_model.third_shift_packing - self.hph_data_model.third_shift_commit) * self.hph_data_model.time_per_unit , 2)
                if self.hph_data_model.third_shift_packing - self.hph_data_model.third_shift_commit < 0
                else 0
        )
        return {
            "smt": status_smt,
            "packing": status_packing
        }



def fetch_data_to_dict(json_data)-> list[HPHDataModel]:
    _data: list[HPHDataModel] = []
    for record in json_data:
        _hours: list[HourDataModel] = []
        for hour in record['expand']['hours']:
            _hour = HourDataModel(
                id=hour.get("id"),
                hour=hour.get("place"),
                smtIn=hour.get("smtIn"),
                smtOut=hour.get("smtOut"),
                packing=hour.get("packing")
            )
            _hours.append(_hour)
        _hph = HPHDataModel(
            id=record.get("id"),
            line=record.get("line"),
            planned_hours=record.get("planed_hours"),
            target_oee=record.get("target_oee"),
            uph=record.get("uph"),
            date=record.get("date"),
            week=record.get("week"),
            platform=record.get("platform"),
            sku=record.get("sku"),
            hours=_hours
        )
        _data.append(_hph)
    return _data

def fetch_data_from_pocketbase():
    # Define the base URL and query parameters
    base_url = "http://10.13.33.46:3030/api/collections/workplan_hours/records"
    params = {
        "filter": "(date = '2024-08-29')",
        "expand": "hours"
    }

    try:
        # Make the GET request
        logging.info("Sending request to PocketBase API...")
        response = requests.get(base_url, params=params, timeout=10)

        # Check for successful status code
        if response.status_code == 200:
            logging.info("Request successful.")
            data = response.json()

            if len(data['items']) > 0:
                return data['items']

            return []
        else:
            logging.error(f"Failed request with status code: {response.status_code}")
            response.raise_for_status()  # Raise an exception for other HTTP errors

    except requests.exceptions.Timeout:
        logging.error("The request timed out.")
    except requests.exceptions.ConnectionError:
        logging.error("There was a network problem (e.g., DNS failure, refused connection).")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        logging.error(f"An error occurred: {err}")
    return None


def get_line_status_model_data():
    data = fetch_data_from_pocketbase()
    model = fetch_data_to_dict(data)
    line_status: list[LineStatusDataModel] = []
    for _m in model:
        line_status.append(
            LineStatusDataModel(
                hph_data_model=_m,
                date=_m.date,
                line=_m.line,
                planned_hours=_m.planned_hours,
                target_oee=_m.target_oee,
                uph=_m.installed_uph,
                output=_m.packing_total,
                commit=_m.commit_units,
                lost_units=_m.units_lost_packing,
                lost_time=_m.lost_time
            )
        )

    production_smt_by_shift = []
    production_packing_by_shift = []


    for ls in line_status:

        production_smt_by_shift.append(ls.first_status['smt'])
        production_smt_by_shift.append(ls.second_status['smt'])
        production_smt_by_shift.append(ls.third_status['smt'])

        production_packing_by_shift.append(ls.first_status['packing'])
        production_packing_by_shift.append(ls.second_status['packing'])
        production_packing_by_shift.append(ls.third_status['packing'])
    return {
        "smt": production_smt_by_shift,
        "packing": production_packing_by_shift
    }



if __name__ == "__main__":
    get_line_status_model_data()
    # data = fetch_data_from_pocketbase()
    # model = fetch_data_to_dict(data)
    # for e in model:
    #     print(e)
