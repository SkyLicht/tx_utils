import json
import re
from datetime import datetime

from scada.fuzion.fuzion_engine import logs_segregation
from scada.fuzion.fuzion_handler import handle_fuzion_log_parse
from utils.file_management_util import su_read_name_of_files_from_path, su_extract_date_from_string, \
    su_dict_group_by, su_dict_to_excel, su_read_file_line, su_dict_to_json, su_save_json_file
from utils.ql_util import qa_transform_str_date, DateFormat


def read_logs_and_extract_for_the_first_record(file_path: str)-> list[dict]:
    _return_files = []
    files_name = su_read_name_of_files_from_path(file_path)
    for file in files_name:
        line = su_read_file_line(f"{file_path}/{file}", 18)
        match = re.search(r'\d{2}/\d{2}/\d{4}', line)
        if match:
            date_str = match.group(0)
            try:
                # Attempt to parse the date based on the matched string format.
                date_obj = datetime.strptime(date_str, '%m/%d/%Y')  # Adjust format to match your pattern
                _return_files.append({
                    "text": file,
                    "date_str": datetime.fromtimestamp(date_obj.timestamp()).strftime('%Y-%m-%d')
                })
            except ValueError:
                print("Error")
    print(_return_files)
    return _return_files




def read_logs_by_date(file_path: str, date: str)-> list[dict]:
    files_names = su_read_name_of_files_from_path(file_path)
    transform_names = [
        info for f in files_names if (info := su_extract_date_from_string(f, r'\d{4}-\d{2}-\d{2}'))
    ]
    parse_data: list[dict] = []
    if transform_names:
        indexes = [i for i, info in enumerate(transform_names) if info['date_str'] == date]

        # Add neighboring indexes if applicable
        if indexes:
            first, last = indexes[0], indexes[-1]
            if first > 0:
                indexes.append(first - 1)
            if last < len(transform_names) - 1:
                indexes.append(last + 1)

            # Sort the final list of indexes
            indexes = sorted(set(indexes))

            for index in indexes:
                print(transform_names[index])
                parse_data.extend(handle_fuzion_log_parse(f"{file_path}/{transform_names[index]['text']}"))



    print(f"Date: {date}")
    print(f"Total records: {len(parse_data)}")

    only_record_that_macht_date = [record for record in parse_data if qa_transform_str_date(record['date'], DateFormat.DATE_FORMAT, DateFormat.SQL_FORMAT) == date]
    print(f"Total records that match the date: {len(only_record_that_macht_date)}")
    # for record in only_record_that_macht_date[:100]:
    #     print(record)
    return only_record_that_macht_date

def read_logs_all():
    file_path = "C:/data/fuzion-1_j01_top"
    files_names = su_read_name_of_files_from_path(file_path)
    transform_names = [info for f in files_names if (info := su_extract_date_from_string(f, r'\d{4}-\d{2}-\d{2}'))]
    if transform_names:
        grouped = su_dict_group_by(transform_names, 'date')
        compile_parse_data = []
        for key, value in grouped.items():
            compile_parse_data_by_date = []
            for info in value:
                parse_data = handle_fuzion_log_parse(f"{file_path}/{info['text']}")
                for data in parse_data:
                    compile_parse_data_by_date.append(data)
            compile_parse_data.append({
                "date": key,
                "data": compile_parse_data_by_date
            })



if __name__ == '__main__':
    _logs = read_logs_by_date("C:/data/fuzion-1_j01_top", "2024-08-20")
    _segregation = logs_segregation(_logs)

    print(json.dumps(_segregation["rejected_componentes"], indent=4))


    # print(json.dumps(_segregation["statistics"], indent=4))


    # for record in _segregation["processes"]:
    #     print(record["time"])

    # for record in _segregation["processes"]:
    #     print(json.dumps(record,indent= 4))

    # print(json.dumps(_segregation["processes"][0], indent=4))

    # for record in _logs:

    # _json = su_dict_to_json(_logs)
    # su_save_json_file(_json, "residuals", "../../files/fuzion/logs")

    # Read json file
    # with open("../../files/fuzion/logs/residuals.json", 'r') as file:
    #     data = file.read()
    #
    #
    # for record in json.loads(data):
    #     print(json.dumps(record, indent=4))
    # su_dict_to_excel(
    #     data= _logs,
    #     file_path= "../../files/fuzion/logs",
    #     file_name= "fuzion_logs",
    #     show= False
    # )





#
# and (date_info := next((info for info in transform_names if info['date_str'] == date), None)):
#         parse_data = handle_fuzion_log_parse(f"{file_path}/{date_info['file_name']}")
#         print(f"Date: {date_info['date']}")
#         print(f"Total records: {len(parse_data)}")
#         return parse_data