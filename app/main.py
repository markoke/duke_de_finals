from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import joblib
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = joblib.load("rf_model.pkl")
label_encoder_district = joblib.load("label_encoder_district.pkl")
label_encoder_sub_county = joblib.load("label_encoder_sub_county.pkl")
label_encoder_air_quality = joblib.load("label_encoder_air_quality.pkl")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Input Data Model
class InputData(BaseModel):
    district: str
    sub_county: str
    latitude: float
    longitude: float

@app.post("/predict")
def predict(input_data: InputData):
    logger.info("Prediction requested with input data: %s", input_data.dict())

    district_encoded = label_encoder_district.transform([input_data.district])[0]
    sub_county_encoded = label_encoder_sub_county.transform([input_data.sub_county])[0]

    X = pd.DataFrame({
        "site_details_district": [district_encoded],
        "site_details_sub_county": [sub_county_encoded],
        "site_details_approximate_latitude": [input_data.latitude],
        "site_details_approximate_longitude": [input_data.longitude]
    })

    prediction = model.predict(X)[0]
    air_quality = label_encoder_air_quality.inverse_transform([prediction])[0]

    logger.info("Prediction result: %s", air_quality)
    return {"prediction": air_quality}

@app.get("/example_predict")
def example_predict():
    example_data = {
        "district": "Kampala",
        "sub_county": "Kawempe division",
        "latitude": 0.348894858768722,
        "longitude": 32.5720024327486
    }
    response = predict(InputData(**example_data))
    return response
