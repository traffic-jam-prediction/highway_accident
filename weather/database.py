import mysql.connector as database
from dotenv import load_dotenv
import os

load_dotenv()
username = os.getenv('username')
password = os.getenv('password')


def save_weather_data_to_database(datetime: str, highway: str, mileage: float, wind_speed: float, temperature: float, humidity: float,):
    print(username,password)
    connection = database.connect(
        user=username,
        password=password,
        host="localhost",
        database="highway")
    cursor = connection.cursor()
    try:
        statement = "INSERT INTO weather (Datetime, Highway, Mileage, WindSpeed, Temperature, Humidity) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (datetime, highway, mileage, wind_speed, temperature, humidity)
        cursor.execute(statement, data)
        connection.commit()
    except database.Error as e:
        print(f"Error adding entry to database: {e}")
