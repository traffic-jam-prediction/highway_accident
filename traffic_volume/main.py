from Integrated_forecastdata import integrated_forecastdata
from dataframe_to_mariadb import save_traffic_dataframe_to_database

if __name__ == '__main__':
    traffic_dataframe = integrated_forecastdata()
    save_traffic_dataframe_to_database(traffic_dataframe)