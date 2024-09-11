from enum import Enum


class FileExtensionName(Enum):
    Excel = 'excel'
    CSV = 'csv'
    JSON = 'json'
    Text = 'txt'

class FileExtensionExcel(Enum):
    Default = 'xlsx'
    XLSX = 'xlsx'
    XLS = 'xls'



def get_file_extension(file_name: str) -> str:
    """ Get the file extension name """
    return file_name.split('.')[-1]