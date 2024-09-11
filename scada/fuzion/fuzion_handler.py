from bs4 import BeautifulSoup


def handle_fuzion_log_parse(file_path: str)-> list[dict]:
    # Re-attempting to read the file with the correct encoding
    with open(file_path, 'r', encoding='utf-16') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the table rows
    rows = soup.find_all('tr')

    # Extract data from the table
    data = []
    for row in rows[1:]:  # Skip the header row
        cols = row.find_all('td')
        data.append([col.text.strip() for col in cols])

    _return_data: list[dict] = [{
            "date": d[0],
            "time": d[1],
            "user": d[2],
            "message": d[3],
            "text": d[4]
        } for d in data]

    return _return_data