import json
from web_scraping import price_data_file, scrape_oil_price
from datetime import date, timedelta

def read_price_data_from_json() -> dict:
    data = None
    with open(price_data_file, 'r') as json_file:
        data = json.load(json_file)
    return data

def data_is_outdated(price_data: dict) -> bool:
    latest_date = None
    for date_string in price_data.keys():
        price_date = date.fromisoformat(date_string)
        if not latest_date or price_date > latest_date:
            latest_date = price_date
    next_price_change_date = latest_date + timedelta(days=7)
    if date.today() > next_price_change_date:
       return True
    else:
        return False

# please give the date_string in ISO format (which is 2023-03-19 for the common used 2023/03/19)
def get_price(date_string: str):
    target_date = date.fromisoformat(date_string)

    oil_price_data = read_price_data_from_json()

    if data_is_outdated(oil_price_data):
        print("updating data ...")
        scrape_oil_price()
        oil_price_data = read_price_data_from_json()

    closest_date = None
    for date_string in oil_price_data.keys():
        price_date = date.fromisoformat(date_string)
        if price_date < target_date and (not closest_date or price_date > closest_date):
            closest_date = price_date
    closest_date_string = date.isoformat(closest_date)
    target_date_oil_price = oil_price_data[closest_date_string]
    return target_date_oil_price
