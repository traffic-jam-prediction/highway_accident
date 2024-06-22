import mysql.connector as database
from file import read_json_file


def get_username_and_password() -> tuple:
    database_authentication = read_json_file("database_authentication.json")
    username = database_authentication["username"]
    password = database_authentication["password"]
    return username, password


def add_data(datetime: str, highway: str, mileage: float, wind_speed: float, temperature: float, humidity: float,):
    connection = database.connect(
        user=username,
        password=password,
        host="localhost",
        database="highway")
    cursor = connection.cursor()
    try:
        statement = "INSERT INTO weather (datetime, highway, mileage, WindSpeed, Temperature, Humidity) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (datetime, highway, mileage, wind_speed, temperature, humidity)
        cursor.execute(statement, data)
        connection.commit()
    except database.Error as e:
        print(f"Error adding entry to database: {e}")


username, password = get_username_and_password()
