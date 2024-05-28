# weather

## how to use

To get weather, you need a pair of app_id and app_key, and save it to tdx_credentials.json, it should look like the following

```json
{
    "app_id": "YOUR_APP_ID",
    "app_key":"YOUR_APP_KEY"
}
```

## save to database

### SQL authentication

- create a json file named ```database_authentication.json``` with the following data
```json
{
    "username": "DATABASE_USER_NAME",
    "password": "DATABASE_USER_PASSWORD"
}
```

### create database

The weather table should be under the highway database

```sql
CREATE DATABASE highway;
USE highway;
```

### create table

```sql
CREATE TABLE weather (
    date DATE,
    time TIME,
    highway VARCHAR(10),
    mileage DOUBLE,
    WDSD DOUBLE,
    Temp DOUBLE,
    HUMD DOUBLE,
    PRES DOUBLE
);
ALTER TABLE weather MODIFY COLUMN highway VARCHAR(10) CHARACTER SET utf8mb4;
```
