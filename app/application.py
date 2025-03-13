from fastapi import FastAPI, File, UploadFile, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger
import pandas as pd
import io
from src.utils.inference.pose_inference import InferenceData

# Khởi tạo FastAPI
app = FastAPI(
    author="Dat Truong",
    title="Detect Sleep State",
    description="Detect sleep state",
    version="0.0.1",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Điều hướng trang chính về /docs
@app.get("/", include_in_schema=False)
async def redirect():
    return RedirectResponse("/docs")

# API kiểm tra trạng thái server
@app.get("/healthcheck", status_code=status.HTTP_200_OK)
def healthcheck():
    return {"healthcheck": "Everything in healthy mode!"}

# API dự đoán trạng thái ngủ
@app.post("/detect_sleep_state")
async def predict(file: UploadFile = File(...)):
    try:
        # Đọc file parquet từ bytes
        contents = await file.read()
        df = pd.read_parquet(io.BytesIO(contents))

        # Khởi tạo InferenceData với mô hình đã lưu
        model_path = "/app/src/weight/random_forest.pkl"  # Đường dẫn model
        inference_model = InferenceData(model_path)

        # Thực hiện dự đoán
        predictions = inference_model.process(df)

        # Trả về kết quả dưới dạng JSON
        return predictions.to_dict(orient="records")

    except Exception as e:
        logger.exception(f"❌ Lỗi trong quá trình dự đoán: {e}")
        raise HTTPException(status_code=500, detail="Errors processing the file")
