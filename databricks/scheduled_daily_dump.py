# Databricks notebook source
# Import necessary libraries
import datetime
import time
import requests
import json
import psycopg2
from pyspark.sql import SparkSession

# COMMAND ----------

# # Check for secret scopes
# mysecrets = dbutils.secrets.listScopes()
# for secret in mysecrets:
#   print(secret.name)

# COMMAND ----------

# Access Keys 
AIRQLOUD_ID = dbutils.secrets.get("airqo", "AIRQLOUDID")
TOKEN = dbutils.secrets.get("airqo", "TOKEN")
USER = dbutils.secrets.get("airqo", "USER")
PASSWORD = dbutils.secrets.get("airqo", "PASSWORD")
HOST = dbutils.secrets.get("airqo", "HOST")
PORT = dbutils.secrets.get("airqo", "PORT")
DATABASE = dbutils.secrets.get("airqo", "DATABASE")


# COMMAND ----------

conn_params = {
    "user": USER,
    "password": PASSWORD,
    "host": HOST,
    "port": int(PORT),  
    "database": DATABASE
}

# COMMAND ----------


url = f"https://api.airqo.net/api/v2/devices/measurements/airqlouds/{AIRQLOUD_ID}/historical"
now = datetime.datetime.now()
start = now - datetime.timedelta(hours=25)
end = now

startTime = start.isoformat()  
endTime = end.isoformat()

params = {
    "startTime": startTime, 
    "endTime": endTime,
    "token": TOKEN
}
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
# print(f"Fetched {len(measurements)} measurements from AirQo API")

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

insert_query = """INSERT INTO measurements VALUES (
    %(device)s, %(device_id)s, %(site_id)s, %(time)s,
    %(pm2_5)s, %(pm10)s, %(frequency)s, %(no2)s, %(site_details)s    
)"""

cursor.executemany(insert_query, measurements)
conn.commit()

# Verify data
cursor.execute("SELECT * FROM measurements")
rows = cursor.fetchall()
print(f"Total Rows On database: {len(rows)}")

# for row in rows:
#    print(row)

cursor.close()
conn.close()
