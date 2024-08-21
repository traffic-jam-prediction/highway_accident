import math
import os
from tdx_api import get_data, get_data_and_save_to_json
from file import write_json_to_file, read_json_file
from haversine import haversine

road_encoding_file = "road_encoding.json"


def split_mileage_into_km_and_m(mileage: float):
    integer_part = math.floor(mileage)
    decimal_part = math.floor((mileage - integer_part)*1000)
    return integer_part, decimal_part


def get_road_class(road: str) -> int:
    road_prefix = road[:2]
    if road_prefix == "國道":
        return 0
    else:
        raise Exception("road not supported")


def get_road_data_from_tdx():
    highway = get_road_class("國道1號")
    road_encoding_api_url = f"https://tdx.transportdata.tw/api/basic/V3/Map/Basic/RoadClass/{highway}?%24format=JSON"
    road_data = get_data(road_encoding_api_url)
    road_encoding = dict()
    for road in road_data:
        road_name = road["RoadName"]
        road_id = road["RoadID"]
        road_encoding[road_name] = road_id
    write_json_to_file(road_encoding_file, road_encoding)


def get_road_id(road_name: str) -> str:
    if not os.path.exists(road_encoding_file):
        get_road_data_from_tdx()
    road_encoding = read_json_file(road_encoding_file)
    return road_encoding[road_name]


def get_mileage_GPS(road_name: str, mileage: float):
    '''
    mileage is in the format of k,
    for example: should return 1.2 for the mileage 1.2k
    '''
    kilometer, meter = split_mileage_into_km_and_m(mileage)
    road_class = get_road_class(road_name)
    if road_name == "國道1號_高架":
        if mileage <= 32.6:
            road_name = "國道1號汐止五股高架道路"
        else:
            road_name = "國道1號五股楊梅高架道路"
    road_id = get_road_id(road_name)
    mileage_to_GPS_api_url = f"https://tdx.transportdata.tw/api/advanced/V3/Map/GeoCode/Coordinate/RoadClass/{road_class}/RoadID/{road_id}/Mileage/{kilometer}K+{meter}?%24format=GEOJSON"
    mileage_data = get_data(mileage_to_GPS_api_url)
    try:
        mileage_GPS = mileage_data["features"][0]["geometry"]["coordinates"]
    except TypeError:
        print(f'{road_name} {mileage}')
        print(mileage_data["features"][0])
    return mileage_GPS[1], mileage_GPS[0]

def haversine_distance(point_1: tuple, point_2: tuple) -> float:
    '''
    point format should be in (LATITUDE, LONGITUDE) format
    '''
    try:
        return haversine(point_1, point_2)
    except:
        print(point_1,point_2)
