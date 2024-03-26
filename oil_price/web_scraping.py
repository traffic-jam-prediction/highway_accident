import requests
from bs4 import BeautifulSoup
import json
from datetime import date

oil_price_history_website_url = 'https://vipmbr.cpc.com.tw/mbwebs/ShowHistoryPrice_oil.aspx'
required_attributes = ["調價日期", "無鉛汽油92", "無鉛汽油95", "無鉛汽油98", "超級/高級柴油"]
required_attributes_english = [
    "date", "gasoline-92", "gasoline-95", "gasoline-98", "diesel_fuel"]
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
price_data_file = 'oil_price.json'

def date_string_to_iso_format(date_string: str) -> date:
    date_number = date_string.split("/")
    year = int(date_number[0])
    month = int(date_number[1])
    day = int(date_number[2])
    string_date = date(year, month, day).isoformat()
    return string_date

def scrape_oil_price():
    attribute_indices = dict()
    oil_price = dict()

    response = requests.get(oil_price_history_website_url, headers=headers)
    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'MyGridView'})

        if table:

            rows = table.find_all('tr')
            # dataframe attribute
            attribute_row = rows[0]
            all_attributes = attribute_row.find_all("th")
            for index, attribute in enumerate(all_attributes):
                attribute_text = attribute.get_text()
                for required_attribute in required_attributes:
                    if attribute_text == required_attribute:
                        attribute_indices[required_attribute] = index

            for i in range(1, len(rows)):
                # for i in range(1, 2):
                row = rows[i]
                cells = row.find_all('td')
                current_date_data = dict()
                date = None
                data_concat = ""
                for index, attribute in enumerate(required_attributes):
                    data_index = attribute_indices[attribute]
                    data = cells[data_index].find("span").get_text()
                    if index == 0:
                        date = date_string_to_iso_format(data)
                    else:
                        data_concat += str(data)
                        current_date_data[attribute] = str(data)
                # make sure there is price change in 92, 95, 98 and diesel fuel
                if data_concat != "":
                    oil_price[date] = current_date_data

            # save json file
            with open(price_data_file, 'w', encoding="utf8") as json_file:
                json.dump(oil_price, json_file, indent=4, ensure_ascii=False)

            print(f"price data saved to {price_data_file}")

        else:
            print("Table with ID 'MyGridView' not found on the page.")
    else:
        print(
            f"Failed to retrieve content. Status code: {response.status_code}")
