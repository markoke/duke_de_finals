import requests
import json
import calendar
from datetime import datetime, timedelta
import psycopg2
import os

airqloud_id = os.environ.get("AIRQLOUD_ID")
token = os.environ.get("TOKEN")

conn_params = {
    "user": os.environ.get("USER"),
    "password": os.environ.get("PASSWORD"),
    "host": os.environ.get("HOST"),
    "port": int(os.environ.get("PORT", 5432)),
    "database": os.environ.get("DATABASE"),
}


url = f"https://api.airqo.net/api/v2/devices/measurements/airqlouds/{airqloud_id}/historical"

# Connect to PostgreSQL
conn = psycopg2.connect(**conn_params)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
      device VARCHAR(100),
      device_id VARCHAR(100),
      site_id VARCHAR(100),
      time TIMESTAMPTZ,
      pm2_5 JSONB,  
      pm10 JSONB,
      frequency VARCHAR(100),   
      no2 JSONB,
      site_details JSONB
    )
""")

# Iterate over months and days
start_date = datetime(2021, 1, 1)
end_date = datetime(2023, 12, 4)

current_date = start_date
while current_date <= end_date:
    _, last_day = calendar.monthrange(current_date.year, current_date.month)
    end_of_month = datetime(current_date.year, current_date.month, last_day)

    params = {"startTime": current_date.strftime("%Y-%m-%d"),
              "endTime": end_of_month.strftime("%Y-%m-%d"), "token": token}

    # Make API request
    response = requests.get(url, params=params)
    data = json.loads(response.text)

    measurements = []
    for measure in data["measurements"]:
        parsed = {
            "device": measure["device"],
            "device_id": measure["device_id"],
            "site_id": measure["site_id"],
            "time": measure["time"],
            "pm2_5": json.dumps(measure["pm2_5"]),
            "pm10": json.dumps(measure["pm10"]),
            "frequency": measure["frequency"],
            "no2": json.dumps(measure["no2"]),
            "site_details": json.dumps(measure["siteDetails"])
        }
        measurements.append(parsed)

    # Insert data into PostgreSQL Azure
    insert_query = """INSERT INTO measurements VALUES (
        %(device)s, %(device_id)s, %(site_id)s, %(time)s,
        %(pm2_5)s, %(pm10)s, %(frequency)s, %(no2)s, %(site_details)s    
    )"""
    cursor.executemany(insert_query, measurements)
    conn.commit()

    # Move to the next month
    current_date = end_of_month + timedelta(days=1)

cursor.close()
conn.close()

