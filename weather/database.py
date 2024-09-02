import mysql.connector as database
from dotenv import load_dotenv
import os

table_name = 'weather'


def save_weather_data_to_database(datetime: str, highway: str, mileage: float, wind_speed: float, temperature: float, humidity: float):
    load_dotenv(dotenv_path=os.path.join(
        os.path.dirname(__file__), '..', '.env'))
    username = os.getenv('username')
    password = os.getenv('password')
    table_name = "weather"

    connection = database.connect(
        user=username,
        password=password,
        host="localhost",
        database="highway")
    cursor = connection.cursor()
    try:
        # Check if the table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        table_exists = cursor.fetchone()

        # If the table doesn't exist, create it
        if not table_exists:
            create_table_query = f"""
            CREATE TABLE {table_name} (
                DateTime DATETIME,
                Highway VARCHAR(10) CHARACTER SET utf8mb4,
                Mileage FLOAT,
                WindSpeed DOUBLE,
                Temperature DOUBLE,
                Humidity DOUBLE,
                UNIQUE (DateTime, Highway, Mileage)
            )
            """
            cursor.execute(create_table_query)
        # Insert data into the table
        insert_query = f"""
        INSERT INTO {table_name} (DateTime, Highway, Mileage, WindSpeed, Temperature, Humidity)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = (datetime, highway, mileage, wind_speed, temperature, humidity)
        cursor.execute(insert_query, data)
        connection.commit()
    except database.Error as e:
        print(f"Error adding entry to database: {e}")
