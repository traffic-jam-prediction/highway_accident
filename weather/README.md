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

### requirements

You need the following libraries

```bash
pip install mysql.connector haversine python-dotenv
```

### SQL authentication

- edit   ```.env``` with your username and password in mysql
