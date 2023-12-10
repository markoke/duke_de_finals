import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Load model
with open("rf_model.pkl", "rb") as f:
    model = pickle.load(f)

# Load label encoders
with open("label_encoder_district.pkl", "rb") as f:
    label_encoder_district = pickle.load(f)

with open("label_encoder_sub_county.pkl", "rb") as f:
    label_encoder_sub_county = pickle.load(f)

with open("label_encoder_air_quality.pkl", "rb") as f:
    label_encoder_air_quality = pickle.load(f)

# Input data
district = "Nairobi"
sub_county = "Westlands"
latitude = -1.2921
longitude = 36.8219

# Transform input data
district_encoded = label_encoder_district.transform([district])
sub_county_encoded = label_encoder_sub_county.transform([sub_county])

X = pd.DataFrame({
    "site_details_district": district_encoded,
    "site_details_sub_county": sub_county_encoded,
    "site_details_approximate_latitude": [latitude],
    "site_details_approximate_longitude": [longitude]
})

# Make prediction
prediction = model.predict(X)[0]

# Inverse transform prediction
air_quality = label_encoder_air_quality.inverse_transform([prediction])[0]

print(air_quality)