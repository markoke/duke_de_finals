import pickle
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# Load model and label encoders
with open("rf_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("label_encoder_district.pkl", "rb") as f:
    label_encoder_district = pickle.load(f)

with open("label_encoder_sub_county.pkl", "rb") as f:
    label_encoder_sub_county = pickle.load(f)

with open("label_encoder_air_quality.pkl", "rb") as f:
    label_encoder_air_quality = pickle.load(f)

app = FastAPI()


class InputData(BaseModel):
    district: str
    sub_county: str
    latitude: float
    longitude: float


@app.post("/predict")
def predict(input_data: InputData):
    X = pd.DataFrame({
        "site_details_district": label_encoder_district.transform([input_data.district]),
        "site_details_sub_county": label_encoder_sub_county.transform([input_data.sub_county]),
        "site_details_approximate_latitude": [input_data.latitude],
        "site_details_approximate_longitude": [input_data.longitude]
    })

    prediction = model.predict(X)[0]
    air_quality = label_encoder_air_quality.inverse_transform([prediction])[0]

    return {"prediction": air_quality}