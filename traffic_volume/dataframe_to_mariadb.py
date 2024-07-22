import pandas as pd
import mariadb
import sys
import json
import numpy as np
from Integrated_forecastdata import integrated_forecastdata

if __name__ == '__main__':
    df = integrated_forecastdata()
    # df = pd.read_csv('main06.csv')
    df.replace({np.nan: None}, inplace=True)
    df['M03A_PCU_BigGap'] = df['M03A_PCU_BigGap'].apply(lambda x: str(x)[:1] if x is not None else None)
    df['Holiday'] = df['Holiday'].apply(lambda x: str(x)[:1] if x is not None else None)

    # Load database authentication details
    try:
        with open('database_authentication.json', 'r') as file:
            db_config = json.load(file)
    except Exception as e:
        print(f"Error loading database authentication details: {e}")
        sys.exit(1)

    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=db_config['username'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database']
        )
        print("Connection successful!") 

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cur = conn.cursor()

    # Create Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS traffic (
            DateTime TIMESTAMP,
            RoadSection VARCHAR(20),
            Highway VARCHAR(10),
            Direction CHAR(1),
            Midpoint FLOAT,
            M03A_PCU FLOAT,
            M03A_PCU_BigGap CHAR(1),
            M05A_SpaceMeanSpeed FLOAT,
            M05A_PCU FLOAT,
            Accident INT(1),
            Holiday CHAR(1),
            Week VARCHAR(10)
        )
    """)

    # Insert Data
    for _, row in df.iterrows():
        sql = """
            INSERT INTO traffic
            (DateTime, RoadSection, Highway, Direction, Midpoint,
            M03A_PCU, M03A_PCU_BigGap, M05A_SpaceMeanSpeed, M05A_PCU, Accident, Holiday, Week) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, tuple(row.values))

    conn.commit()
    conn.close()

    print("DataFrame successfully written to MariaDB")
