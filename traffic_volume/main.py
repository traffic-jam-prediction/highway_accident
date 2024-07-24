from Integrate_traffic_data import integrate_traffic_data
from dataframe_to_mariadb import save_traffic_dataframe_to_database

if __name__ == '__main__':
    traffic_dataframe = integrate_traffic_data()
    save_traffic_dataframe_to_database(traffic_dataframe)