import fitz  # from PyMuPDF
import json
import re
import requests
import os
import pandas as pd

pdf_file_path = 'TDCS使用手冊v34.pdf'

def download_documentation_pdf():
    documentation_url = "https://tisvcloud.freeway.gov.tw/documents/TDCS%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8Av34.pdf"
    response = requests.get(documentation_url)

    if response.status_code == 200:
        with open(pdf_file_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(
            f"Failed to download the documentation. Status code: {response.status_code}")

def delete_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except PermissionError:
        print(f"Permission error. Unable to delete file: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    doc.close()
    return text


def extract_GantryID_table(pdf_text: str) -> list:
    table_column = "偵測站代碼 說明 "
    table_index = pdf_text.find(table_column)
    # +1 skips the newline
    table_text = pdf_text[table_index + len(table_column)+1:]
    table_list = table_text.split("\n")
    return table_list

def extract_M03A_attributes(pdf_text: str) -> str:
    m03A_paragraph_index = pdf_text.find("報表代號：M03A")
    m04A_paragraph_index = pdf_text.find("報表代號：M04A")
    return pdf_text[m03A_paragraph_index:m04A_paragraph_index]


def remove_space(string: str) -> str:
    string = string.replace(" ", "")
    return string


def get_alphabet_index(string: str) -> list:
    indices = [match.start() for match in re.finditer(r'[A-Z]', string)]
    return indices


gantryID_example = "05F0287S"
gantryID_example_length = len(gantryID_example)



def is_valid_gantryID(gantryID: str) -> bool:
    gantryID_length = len(gantryID)
    if gantryID_length != gantryID_example_length:
        return False
    alphabet_indices = get_alphabet_index(gantryID_example)
    for index in alphabet_indices:
        if gantryID[index] < "A" or gantryID[index] > "Z":
            return False
    return True


def is_composed_of_chinese_characters(string: str) -> bool:
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
    return bool(chinese_pattern.fullmatch(string))


def is_valid_road_segment(road_segment: str) -> bool:
    road_segment = road_segment.replace(
        "(", "").replace(")", "").replace("&", "")
    road_edges = road_segment.split("-")
    return len(road_edges) >= 2 and is_composed_of_chinese_characters(road_edges[0]) and is_composed_of_chinese_characters(road_edges[1])


def is_numeric_digit(char):
    return '0' <= char <= '9'


def extract_gantryID_from_table(table: list) -> list:
    gantryID_list = []
    for text in table:
        text = remove_space(text)
        if text == "":
            continue
        if is_valid_gantryID(text):
            gantryID_list.append(text)
        elif is_valid_road_segment(text):
            continue
        elif len(text) >= gantryID_example_length and is_numeric_digit(text[0]):
            text_top = text[:gantryID_example_length]
            if is_valid_gantryID(text_top):
                gantryID_list.append(text_top)
    return gantryID_list



def gantryID_roadsection_mapping()-> list:
    table = extract_GantryID_table(pdf_text)
    gantryID_list = extract_gantryID_from_table(table)

    mapping = {}
    for gantryID in gantryID_list: 
        first_three_digits = gantryID[:3]
        if first_three_digits in ['01F','01H','03F','05F']:
            if gantryID[2:3] == 'H':
                 csv_file = f"../highway_ information/國道1號_高架.csv"
            else:
                highway = gantryID[1:2]
                csv_file = f"../highway_ information/國道{highway}號.csv"

            if gantryID[3:4] == 'R':
                kilometer = int(gantryID[4:7])/10
            else:
                kilometer = int(gantryID[3:7])/10

            df = pd.read_csv(csv_file, encoding='utf-8')
            for index, row in df.iterrows():      
                if row['里程K+000'] <= kilometer <= df.iloc[index+1]['里程K+000']:
                    roadsection = f"{row['設施名稱']}-{ df.iloc[index+1]['設施名稱']}"
                    mapping[gantryID] = roadsection
                     
        else:
            continue
    
    return mapping




def get_direction(attributes_text: str) -> dict:
    # narrow down to direction paragraph
    direction_index = attributes_text.find("Direction：")
    vehicle_type_index = attributes_text.find("VehicleType：")
    direction_paragraph = attributes_text[direction_index:vehicle_type_index]

    # narrow down to text inside the parenthesis
    #               +1 to exclude the (
    direction_start_index = direction_paragraph.find("(")+1
    direction_end_index = direction_paragraph.find(")")

    direction_pair_text = direction_paragraph[direction_start_index:direction_end_index]
    direction_pairs = direction_pair_text.split("；")

    direction = dict()
    # direction_pair example->'S：南'
    for direction_pair in direction_pairs:
        direction_pair = direction_pair.split("：")
        if direction_pair[1] == "北":
            direction_pair[1] += "上"
        else:
            direction_pair[1] += "下"
        direction[direction_pair[0]] = direction_pair[1]
    return direction


def get_vehicle_number_and_name(vehicle_mapping: str) -> list:
    left_parenthesis_index = vehicle_mapping.find("(")
    right_parenthesis_index = vehicle_mapping.find(")")
    vehicle_number = vehicle_mapping[:left_parenthesis_index]
    vehicle_name = vehicle_mapping[left_parenthesis_index +
                                   1:right_parenthesis_index]
    return vehicle_number, vehicle_name


def get_vehicle_type(attributes_text: str) -> dict:
    # narrow down to vehicle type paragraph
    vehicle_type_index = attributes_text.find("車種")
    traffic_volume_index = attributes_text.find("交通量：")
    vehicle_type_paragraph = attributes_text[vehicle_type_index:traffic_volume_index]

    # narrow down to real data
    start_index = re.search(r'\d+', vehicle_type_paragraph).start()
    end_index = vehicle_type_paragraph.rfind(")")
    vehicle_type_paragraph = vehicle_type_paragraph[start_index:end_index+1]

    vehicle_mapping_list = vehicle_type_paragraph.split(" 、")
    vehicle = dict()
    for vehicle_mapping in vehicle_mapping_list:
        vehicle_number, vehicle_name = get_vehicle_number_and_name(
            vehicle_mapping)
        vehicle[vehicle_number] = vehicle_name
    return vehicle


if __name__ == '__main__':

    download_documentation_pdf()
    pdf_text = read_pdf(pdf_file_path)
    attribute_detail = dict()
    # RoadSection
    RoadSection = gantryID_roadsection_mapping()
    attribute_detail["RoadSection"] = RoadSection
    # direction and vehicle type
    M03A_attributes_text = extract_M03A_attributes(pdf_text)
    direction = get_direction(M03A_attributes_text)
    vehicle_type = get_vehicle_type(M03A_attributes_text)
    attribute_detail["Direction"] = direction
    attribute_detail["VehicleType"] = vehicle_type
    # save to json
    traffic_volume_attributes_file = "traffic_volume_attributes.json"
    with open(traffic_volume_attributes_file, 'w', encoding="utf8") as json_file:
        json.dump(attribute_detail, json_file,
                  indent=2, ensure_ascii=False)

    delete_file(pdf_file_path)
    print("數據已保存到 'traffic_volume_attributes.json'")