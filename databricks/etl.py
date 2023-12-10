# Databricks notebook source
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import year, month, dayofmonth, hour, col, avg, lag, get_json_object
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql.window import Window 
import pandas as pd
from pandas import json_normalize
import psycopg2

USER = dbutils.secrets.get("airqo", "USER")
PASSWORD = dbutils.secrets.get("airqo", "PASSWORD")  
HOST = dbutils.secrets.get("airqo", "HOST")
PORT = dbutils.secrets.get("airqo", "PORT")
DATABASE = dbutils.secrets.get("airqo", "DATABASE")
 
conn_params = {
  "user": USER,
  "password": PASSWORD,
  "host": HOST,
  "port": int(PORT),
  "database": DATABASE  
}

# COMMAND ----------

OUTPUT_FILE_LOCATION = "/FileStore/tables/airqo/final_ml_data.csv"

# COMMAND ----------

conn = psycopg2.connect(**conn_params)
cursor = conn.cursor()
cursor.execute("SELECT * FROM measurements") 
rows = cursor.fetchall()

columns = ["device", "device_id", "site_id", "time", "pm2_5", "pm10", "frequency", "no2", "site_details"]
df_pd = pd.DataFrame(rows, columns=columns)

# COMMAND ----------

pm2_5_df = json_normalize(df_pd['pm2_5'])
pm2_5_df.columns = [f'pm2_5_{col}' for col in pm2_5_df.columns]
site_details_df = json_normalize(df_pd['site_details'])
site_details_df.columns = [f'site_details_{col}' for col in site_details_df.columns]
result_df = pd.concat([df_pd, pm2_5_df, site_details_df], axis=1)
data = result_df.drop(['pm2_5', 'pm10', 'frequency', 'no2', 'site_details'], axis=1)
data = data.drop_duplicates()

# COMMAND ----------

selected_columns = ['time', 'site_details_district','site_details_sub_county' , 'site_details_approximate_latitude', 'site_details_approximate_longitude', 'pm2_5_value']
final_ml_data = data[selected_columns]
final_ml_data=spark.createDataFrame(final_ml_data) 
final_ml_data.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(OUTPUT_FILE_LOCATION)
