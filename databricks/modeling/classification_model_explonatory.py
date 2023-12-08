# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import pandas as pd

# COMMAND ----------

spark = SparkSession.builder.appName("DeepARForecast").getOrCreate()

# COMMAND ----------

# Reading the dataset
data = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/FileStore/tables/airqo/final_ml_data.csv")
#data = data.withColumn("timestamp", data["time"].cast("timestamp"))

# COMMAND ----------

data_pd = data.toPandas()
def classify_air_quality(pm2_5_value):
    if pm2_5_value <= 50:
        return "Good"
    elif pm2_5_value <= 100:
        return "Moderate"
    elif pm2_5_value <= 200:
        return "Unhealthy"
    elif pm2_5_value <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

data_pd["air_quality"] = data_pd["pm2_5_value"].apply(classify_air_quality)

# COMMAND ----------

data_pd = data_pd[["site_details_district", "site_details_sub_county", "site_details_approximate_latitude", "site_details_approximate_longitude", "air_quality"]]
data_pd = data_pd.dropna()
data_pd.head()

# COMMAND ----------

from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
data_pd["site_details_district"] = label_encoder.fit_transform(data_pd["site_details_district"])
data_pd["site_details_sub_county"] = label_encoder.fit_transform(data_pd["site_details_sub_county"])
data_pd["air_quality"] = label_encoder.fit_transform(data_pd["air_quality"])

# COMMAND ----------

from sklearn.model_selection import train_test_split
X = data_pd[["site_details_district", "site_details_sub_county", "site_details_approximate_latitude", "site_details_approximate_longitude"]]
y = data_pd["air_quality"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
from sklearn.metrics import accuracy_score
accuracy_score(y_test, y_pred)

# COMMAND ----------

# save the model
import pickle
pickle.dump(model, open("rf_model.pkl", "wb"))
