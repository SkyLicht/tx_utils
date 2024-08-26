import json

import pandas as pd
from icecream import ic

from andon.models import get_refined_andons
from utils.file_management import su_read_excel_file


def main():
    ic("Hello, World!")
    data = su_read_excel_file("../files/andons/in/new_andons.xlsx")

    _list_data = get_refined_andons(data).to_list()

    df = pd.DataFrame(_list_data)

    # Save to Excel
    df.to_excel("../files/andons/out/andon_report.xlsx", index=False)


    ic(df)

if __name__ == "__main__":
    main()