import mysql.connector as database
from file import read_json_file


def get_username_and_password() -> tuple:
    database_authentication = read_json_file("database_authentication.json")
    username = database_authentication["username"]
    password = database_authentication["password"]
    return username, password


def add_data(date: str, time: str, highway: str, mileage: float, wind_speed: float, temperature: float, humidity: float, pressure: float):
    connection = database.connect(
        user=username,
        password=password,
        host="localhost",
        database="highway")
    cursor = connection.cursor()
    try:
        statement = "INSERT INTO weather (date, time, highway, mileage, WDSD, Temp, HUMD, PRES) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        data = (date, time, highway, mileage, wind_speed,
                temperature, humidity, pressure)
        cursor.execute(statement, data)
        connection.commit()
    except database.Error as e:
        print(f"Error adding entry to database: {e}")


username, password = get_username_and_password()
