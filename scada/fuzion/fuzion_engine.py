import json
from datetime import datetime
from enum import Enum
from itertools import cycle
from os import system
import uuid
from utils.file_management_util import su_save_json_file
from utils.ql_util import qa_transform_str_time_subtract, qa_transform_seconds_to


class EventCode(Enum):
    EVENT_30004 = 30004
    EVENT_30005 = 30005
    EVENT_30006 = 30006
    EVENT_30007 = 30007
    EVENT_30019 = 30019
    EVENT_30025 = 30025
    EVENT_30026 = 30026
    EVENT_30035 = 30035
    EVENT_30037 = 30037
    EVENT_30038 = 30038
    EVENT_30039 = 30039
    EVENT_30040 = 30040
    EVENT_30044 = 30044
    EVENT_30046 = 30046
    EVENT_30055 = 30055
    EVENT_30057 = 30057
    EVENT_30058 = 30058
    EVENT_30059 = 30059
    EVENT_30067 = 30067
    EVENT_30068 = 30068
    EVENT_30069 = 30069
    EVENT_30070 = 30070
    EVENT_30071 = 30071
    EVENT_30072 = 30072 # Machine stopped by operator.
    EVENT_30073 = 30073
    EVENT_30133 = 30133
    EVENT_30134 = 30134
    EVENT_30135 = 30135
    EVENT_30152 = 30152
    EVENT_30153 = 30153
    EVENT_30157 = 30157
    EVENT_30159 = 30159
    EVENT_30161 = 30161
    EVENT_30164 = 30164
    EVENT_30165 = 30165
    EVENT_30168 = 30168
    EVENT_30181 = 30181
    EVENT_30212 = 30212
    EVENT_30216 = 30216
    EVENT_30219 = 30219
    EVENT_30221 = 30221
    EVENT_30223 = 30223
    EVENT_30224 = 30224
    EVENT_30226 = 30226
    EVENT_30227 = 30227
    EVENT_30228 = 30228
    EVENT_30229 = 30229
    EVENT_30232 = 30232
    EVENT_30262 = 30262
    EVENT_30297 = 30297
    EVENT_30327 = 30327
    EVENT_30328 = 30328
    EVENT_30342 = 30342
    EVENT_30344 = 30344
    EVENT_30353 = 30353
    EVENT_30376 = 30376
    EVENT_30381 = 30381
    EVENT_30429 = 30429
    EVENT_30433 = 30433
    EVENT_30434 = 30434
    EVENT_30461 = 30461
    EVENT_30462 = 30462
    EVENT_30463 = 30463
    EVENT_30465 = 30465
    EVENT_30469 = 30469
    EVENT_30573 = 30573
    EVENT_30574 = 30574
    EVENT_30575 = 30575
    EVENT_30577 = 30577
    EVENT_30620 = 30620
    EVENT_30694 = 30694
    EVENT_30695 = 30695
    EVENT_30702 = 30702
    EVENT_30703 = 30703
    EVENT_30704 = 30704
    EVENT_30718 = 30718
    EVENT_30728 = 30728
    EVENT_30794 = 30794
    EVENT_30808 = 30808
    EVENT_30809 = 30809
    EVENT_30816 = 30816
    EVENT_30818 = 30818
    EVENT_30848 = 30848
    EVENT_30870 = 30870
    EVENT_30914 = 30914
    EVENT_30700 = 30700
    EVENT_30701 = 30701
    EVENT_30075 = 30075
    EVENT_30544 = 30544
    EVENT_30742 = 30742
    EVENT_30801 = 30801
    EVENT_30033 = 30033
    EVENT_30200 = 30200
    EVENT_30960 = 30960
    EVENT_30356 = 30356
    EVENT_30807 = 30807
    EVENT_30888 = 30888
    EVENT_30162 = 30162
    EVENT_30886 = 30886
    EVENT_30325 = 30325
    EVENT_30036 = 30036
    EVENT_30355 = 30355
    EVENT_30724 = 30724
    EVENT_30723 = 30723
    EVENT_30141 = 30141
    EVENT_30878 = 30878
    EVENT_30142 = 30142
    EVENT_30883 = 30883
    EVENT_30884 = 30884
    EVENT_30727 = 30727
    DEBUG = 0
    NONE = -1


def find_event_code(event_code: int) -> EventCode:
    return EventCode(event_code)

def logs_segregation(data: list[dict])-> dict:
    sorted_by_time = sorted(data, key=lambda x: x['time'])
    _processes = {
        "processes": [],
        "statistics": {
            "fist_process_hour": None,
            "last_process_hour": None,
            "total_processes": 0.0,
            "total_system_logs": 0,
            "total_idle_logs": 0,
            "total_time": 0.0,
            "total_idle_time": 0.0,
            "total_process_time": 0.0,
            "average_process_time": 0.0,
            "top_ten_process": {
                "summary": {
                    "total_time": 0.0,
                    "total_idle_time": 0.0,
                    "total_process_time": 0.0
                },
                "processes_id": []
            },
            "per_hour": [],
        },
        "rejected_componentes": None
    }
    # Rejected components
    _rejected_components = []
    # Find the start of a process
    start_of_process = None
    finsh_of_process = None
    system_logs = []
    idle_logs = []
    for record in sorted_by_time:
        event_code = transform_message_to_event_code(record['message'])
        if event_code:
            # Rejected components ...
            if event_code == EventCode.EVENT_30161:
                _rejected_components.append(record)
            if start_of_process is None and finsh_of_process is None and event_code == EventCode.EVENT_30044:
                system_logs = []
                idle_logs = []
                system_logs.append(record)
                start_of_process = record['time']
            elif start_of_process is None and finsh_of_process is None:
                idle_logs.append(record)
            else:
                if start_of_process and finsh_of_process is None and event_code != EventCode.EVENT_30037:
                    system_logs.append(record)
                elif start_of_process and finsh_of_process is None and event_code == EventCode.EVENT_30037:
                    finsh_of_process = record['time']
                    system_logs.append(record)
                    _processes["processes"].append({
                        "id": str(uuid.uuid4())[:8],
                        "start": start_of_process,
                        "finish": finsh_of_process,
                        "time":
                            (datetime.strptime(finsh_of_process, "%H:%M:%S")
                             - datetime.strptime(start_of_process, "%H:%M:%S")).seconds,
                        # "idle_time": qa_transform_str_time_subtract(idle_logs[0]['time'], idle_logs[-1]['time']),
                        "system_logs_count": len(system_logs),
                        "idle_logs_count": len(idle_logs),
                        "system_logs": system_logs,
                        "idle_logs": idle_logs
                    })
                    start_of_process = None
                    finsh_of_process = None

    for process in _processes["processes"]:
        process["idle_time"] = qa_transform_str_time_subtract(process["system_logs"][-1]['time'], process["idle_logs"][-1]['time'])

    _processes["statistics"]["total_processes"] = len(_processes["processes"])
    _processes["statistics"]["total_system_logs"] = sum([len(process["system_logs"]) for process in _processes["processes"]])
    _processes["statistics"]["total_idle_logs"] = sum([len(process["idle_logs"]) for process in _processes["processes"]])
    _processes["statistics"]["total_time"] = qa_transform_seconds_to(sum([process["time"] for process in _processes["processes"]]),1)
    _processes["statistics"]["fist_process_hour"] = _processes["processes"][0]["start"]
    _processes["statistics"]["last_process_hour"] = _processes["processes"][-1]["finish"]
    _processes["statistics"]["total_idle_time"] = qa_transform_seconds_to(sum([process["idle_time"] for process in _processes["processes"]]),1)
    _processes["statistics"]["total_process_time"] = (
            qa_transform_seconds_to(sum([process["time"] for process in _processes["processes"]]),1) + _processes["statistics"]["total_idle_time"])
    _processes["statistics"]["average_process_time"] = round(sum([process["time"] for process in _processes["processes"]]) / len([process["time"] for process in _processes["processes"]]),2)
    _processes["processes"].sort(key=lambda x: x['time'], reverse=True)

    _processes["statistics"]["top_ten_process"] = {
        "summary": {
            "total_time": sum([process["time"] for process in _processes["processes"][:10]]),
            "total_idle_time": sum([process["idle_time"] for process in _processes["processes"][:10]]),
            "total_process_time": sum([process["time"] for process in _processes["processes"][:10]]) + sum([process["idle_time"] for process in _processes["processes"][:10]])
        },
        "processes_id": [process["id"] for process in _processes["processes"][:10]]
    }

    _processes["statistics"]["per_hour"] = cycle_time_per_hour(_processes["processes"])

    _processes["rejected_componentes"] = rejected_components(_rejected_components)
    return _processes
def logs_analyser(data: dict):
    pass

def rejected_components(data: list[dict])-> dict:
    _total = 0
    for record in data:
        print(str(record['text']).split(".")[1].split(':')[1]) # Component
        print(str(record['text']).split(".")[2].split(':')[1]) # Reference
        print(str(record['text']).split(".")[3].split(':')[1]) # Reference
        print(str(record['text']).split(".")[4].split(':')[1]) # Reference
    return {
        "total": _total
    }
def cycle_time_per_hour(data: list[dict])-> list[dict]:
    # Group the data by hour. e.g. 00:00:00 - 01:00:00

    _grouped = {}
    for record in data:
        _hour = record['start'].split(':')[0]
        if _hour not in _grouped:
            _grouped[_hour] = []
        _grouped[_hour].append(record)

    _cycle_time_per_hour = []
    for key, value in _grouped.items():
        _cycle_time_per_hour.append({
            "hour": key,
            "total_time": qa_transform_seconds_to(sum([record['time'] for record in value]),0),
            "idle_time": qa_transform_seconds_to(3600 - sum([record['time'] for record in value]) ,0),
            "total_processes": len(value),
            "cycle_time": round(sum([record['time'] for record in value]) /len(value), 2),
            "max_time": max([record['time'] for record in value]),
            "min_time": min([record['time'] for record in value]),
            "top_ten_process_id": [record['id'] for record in sorted(value, key=lambda x: x['time'], reverse=True)[:10]],
            # "top_ten_process": [{
            #     "id": record['id'],
            #     "time": record['time'],
            #     "start": record['start'],
            #     "finish": record['finish'],
            #     "system_logs_count": record['system_logs_count'],
            #     "idle_logs_count": record['idle_logs_count'],
            # } for record in sorted(value, key=lambda x: x['time'], reverse=True)[:4]],
        })

    return _cycle_time_per_hour

def transform_message_to_event_code(message: str) -> EventCode | None:
    # Extract the event code from the message
    if (
            len(message.split(' ')) == 3 and
            message.split(' ')[0] == "Event" and
            message.split(' ')[2].isnumeric() and
            len(message.split(' ')[2]) == 5
    ):
        event_code = message.split(' ')[2]
        _event_code = None
        try:
            _event_code = EventCode(int(event_code))
        except ValueError:
            print(f"Error: {event_code}")
        return _event_code
    elif message == "Debug":
        return EventCode.DEBUG
    else:
        return EventCode.NONE



