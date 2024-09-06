import mysql.connector
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
MYSQL_USER = os.getenv('username')
MYSQL_PASSWORD = os.getenv('password')
MYSQL_DATABASE = os.getenv('database')

# Configurable constants
TEMP_DIR = "/var/lib/mysql-temp-files"
OUTPUT_DIR = "/home/argentum11/Documents"


def get_connection():
    return mysql.connector.connect(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        autocommit=True
    )


def execute_query(query, action: str):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                if action.startswith('select'):
                    return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error in {action}: {err}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False
    except Exception as e:
        print(f"Unexpected error in {action}: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False
    else:
        print(f"{action} successfully.")
        return True


def copy_file(src, dst):
    try:
        with open(src, 'r') as source_file:
            content = source_file.read()
        with open(dst, 'w') as dest_file:
            dest_file.write(content)
        print(f"File copied from {src} to {dst}")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False


for month in range(1, 10):
    print(f"Processing month {month}")

    create_table_query = f"""
    DROP TABLE IF EXISTS traffic_weather_{month};
    CREATE TABLE traffic_weather_{month} (
        DateTime DATETIME,
        RoadSection VARCHAR(20) CHARACTER SET utf8mb4,
        Highway VARCHAR(10) CHARACTER SET utf8mb4,
        Direction CHAR(1),
        Midpoint FLOAT,
        M03A_PCU FLOAT,
        M03A_PCU_BigGap CHAR(1),
        M05A_SpaceMeanSpeed FLOAT,
        M05A_PCU FLOAT,
        Accident INT(1),
        Holiday CHAR(1),
        Week VARCHAR(10),
        WindSpeed DOUBLE,
        Temperature DOUBLE,
        Humidity DOUBLE,
        UNIQUE (DateTime, Highway, Midpoint, Direction)
    );
    """

    insert_data_query = f"""
    INSERT INTO traffic_weather_{month} (DateTime, RoadSection, Highway, Direction, Midpoint, 
        M03A_PCU, M03A_PCU_BigGap, M05A_SpaceMeanSpeed, M05A_PCU, Accident, Holiday, Week, 
        WindSpeed, Temperature, Humidity)
    SELECT t1.DateTime, t1.RoadSection, t1.Highway, t1.Direction, t1.Midpoint, t1.M03A_PCU, 
           t1.M03A_PCU_BigGap, t1.M05A_SpaceMeanSpeed, t1.M05A_PCU, t1.Accident, t1.Holiday, 
           t1.Week, t2.WindSpeed, t2.Temperature, t2.Humidity
    FROM traffic{month} t1
    JOIN weather{month} t2
    ON t1.DateTime = t2.DateTime AND t1.Highway = t2.Highway AND t1.Midpoint = t2.mileage;
    """

    export_to_csv_query = f"""
    SELECT 'DateTime', 'RoadSection', 'Highway', 'Direction', 'Midpoint', 'M03A_PCU', 
           'M03A_PCU_BigGap', 'M05A_SpaceMeanSpeed', 'M05A_PCU', 'Accident', 'Holiday', 
           'Week', 'WindSpeed', 'Temperature', 'Humidity'
    UNION ALL
    SELECT IFNULL(DateTime, ''), IFNULL(RoadSection, ''), IFNULL(Highway, ''), IFNULL(Direction, ''), 
           IFNULL(Midpoint, ''), IFNULL(M03A_PCU, ''), IFNULL(M03A_PCU_BigGap, ''), 
           IFNULL(M05A_SpaceMeanSpeed, ''), IFNULL(M05A_PCU, ''), IFNULL(Accident, ''), 
           IFNULL(Holiday, ''), IFNULL(Week, ''), IFNULL(WindSpeed, ''), IFNULL(Temperature, ''), 
           IFNULL(Humidity, '')
    FROM traffic_weather_{month}
    INTO OUTFILE '{TEMP_DIR}/traffic_weather_{month}.csv'
    FIELDS TERMINATED BY ',' 
    OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\\n';
    """

    # Execute queries
    if not execute_query(create_table_query, 'create new table'):
        continue

    if not execute_query(insert_data_query, 'insert traffic data and weather data into new table'):
        continue

    if not execute_query(export_to_csv_query, 'export to csv'):
        continue

    # Copy the file to the output directory
    src_file_path = f"{TEMP_DIR}/traffic_weather_{month}.csv"
    dst_file_path = f"{OUTPUT_DIR}/traffic_weather_{month}.csv"

    if os.path.exists(src_file_path):
        if copy_file(src_file_path, dst_file_path):
            print(f"File successfully copied to {dst_file_path}")
        else:
            print(
                f"Failed to copy file from {src_file_path} to {dst_file_path}")
    else:
        print(f"Source file not found: {src_file_path}")

    print(f"Completed processing for month {month}")

print("All months processed successfully.")
