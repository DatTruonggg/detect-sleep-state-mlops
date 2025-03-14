from fastapi import FastAPI, File, UploadFile, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger
import pandas as pd
import io
import mlflow
from mlflow.tracking import MlflowClient
from src.utils.inference.pose_inference import InferenceData

# Initialize FastAPI
app = FastAPI(
    title="Detect Sleep State",
    description="API for detecting sleep state using MLflow models",
    version="0.0.1",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Redirect the root endpoint to /docs
@app.get("/", include_in_schema=False)
async def redirect():
    return RedirectResponse("/docs")

# API to check server health status
@app.get("/healthcheck", status_code=status.HTTP_200_OK)
def healthcheck():
    return {"healthcheck": "Everything is running smoothly!"}

# API for sleep state prediction
@app.post("/detect_sleep_state")
async def predict(file: UploadFile = File(...)):
    try:
        logger.info(f"📂 Received file: {file.filename}")

        # Read the Parquet file from bytes
        contents = await file.read()
        df = pd.read_parquet(io.BytesIO(contents))

        # Validate input data
        if df.empty:
            raise ValueError("❌ The input data is empty!")

        # Initialize InferenceData with the registered MLflow model
        inference_model = InferenceData(model_path="./src/weight/random_forest.pkl")
        # Perform prediction
        predictions = inference_model.process(df)

        logger.info(f"✅ Prediction completed on {len(df)} data rows.")

        # Return results as JSON
        return predictions.to_dict(orient="records")

    except ValueError as ve:
        logger.error(f"❌ Data Error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"❌ Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Error processing the file")
