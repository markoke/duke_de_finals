# Local classification model experiment
from pyspark.sql import SparkSession
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import joblib

spark = SparkSession.builder.appName("local_model").getOrCreate()
# Reading the dataset
data = (spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load("../duke_de_finals/data/data.csv"))

data_pd = data.toPandas()
#print(data_pd.head())

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

data_pd = data_pd[["site_details_district", "site_details_sub_county",
                   "site_details_approximate_latitude",
                   "site_details_approximate_longitude", "air_quality"]]
data_pd = data_pd.dropna()
data_pd.head()

from sklearn.preprocessing import LabelEncoder
label_encoder_district = LabelEncoder()
label_encoder_sub_county = LabelEncoder()
label_encoder_air_quality = LabelEncoder()
data_pd["site_details_district"] = (label_encoder_district.
                                    fit_transform(data_pd["site_details_district"]))
data_pd["site_details_sub_county"] = (label_encoder_sub_county.
                                      fit_transform(data_pd["site_details_sub_county"]))
data_pd["air_quality"] = (label_encoder_air_quality.
                          fit_transform(data_pd["air_quality"]))

X = data_pd[["site_details_district", "site_details_sub_county",
             "site_details_approximate_latitude",
             "site_details_approximate_longitude"]]
y = data_pd["air_quality"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(accuracy_score(y_test, y_pred))

# Save the model and label encoders to a local directory
model_path = "app/rf_model.pkl"
label_encoder_district_path = "app/label_encoder_district.pkl"
label_encoder_sub_county_path = "app/label_encoder_sub_county.pkl"
label_encoder_air_quality_path = "app/label_encoder_air_quality.pkl"

joblib.dump(model, model_path)
joblib.dump(label_encoder_district, label_encoder_district_path)
joblib.dump(label_encoder_sub_county, label_encoder_sub_county_path)
joblib.dump(label_encoder_air_quality, label_encoder_air_quality_path)

#data_pd.to_csv("../duke_de_finals/data/final_data.csv", index=False)