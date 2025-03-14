import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.tracking import MlflowClient
from src.utils.feature.feature_extractor import make_features
from itertools import groupby
import joblib
from loguru import logger

class InferenceData:
    def __init__(self, model_path: str):
        """
        Load the model from MLflow Model Registry using alias.
        
        :param model_name: The name of the registered model in MLflow.
        :param model_stage: The alias of the model to load (e.g., 'current', 'Production', 'Staging').
        """
        try:
            # mlflow_tracking_uri = "http://mlflow-sever:5000"  
            # mlflow.set_tracking_uri(mlflow_tracking_uri)

            # client = MlflowClient()
            # model_version_info = client.get_model_version_by_alias(model_name, model_stage)
            # model_version = model_version_info.version
            # model_uri = f"models:/{model_name}/{model_version}"
            
            # # Load model
            # model_path = mlflow.sklearn.load_model(model_uri) 
            # logger.info(f"MODEL TYPE: {model_path}")

            # self.model = joblib.load(f"{model_path}")
            # logger.info(f"✅ Loaded model '{model_name}' version {model_version} from MLflow ({model_stage} alias).")
            logger.info("Use the local .pkl")
            self.model = joblib.load(f"{model_path}")           
            
        except Exception as e:
            logger.info(f"Error: {e}")
            
        self.features = [
            "hour", "anglez", "anglez_rolling_mean", "anglez_rolling_max", "anglez_rolling_std",
            "anglez_diff", "anglez_diff_rolling_mean", "anglez_diff_rolling_max",
            "enmo", "enmo_rolling_mean", "enmo_rolling_max", "enmo_rolling_std",
            "enmo_diff", "enmo_diff_rolling_mean", "enmo_diff_rolling_max",
        ]

    @staticmethod
    def get_event(df):
        """
        Xác định các sự kiện wake-up và onset dựa trên 'smooth' label.
        """
        lst_cv = zip(df.series_id, df.smooth)
        lst_poi = []

        for (c, v), g in groupby(lst_cv, lambda cv: (cv[0], cv[1] != 0 and not pd.isnull(cv[1]))):
            llg = sum(1 for _ in g)
            if not v:
                lst_poi.extend([0] * llg)
            else:
                lst_poi.extend([1] + [0] * (llg - 2) + [1] if llg > 1 else [0])  # 1 -> wakeup, 0 -> onset

        return lst_poi

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Xử lý dữ liệu đầu vào, trích xuất features và thực hiện inference.
        Trả về DataFrame chứa ['series_id', 'step', 'event'].
        """
        if data.empty:
            raise ValueError("❌ Input data is empty! Please provide valid data.")

        # Tiền xử lý dữ liệu
        preprocess_data = make_features(data)

        # Kiểm tra xem có thiếu feature nào không
        missing_features = [f for f in self.features if f not in preprocess_data.columns]
        if missing_features:
            raise ValueError(f"❌ Missing the following required features: {missing_features}")

        # Chuẩn bị dữ liệu cho model
        preprocess_data_test = preprocess_data[self.features]

        # Dự đoán xác suất
        probabilities = self.model.predict_proba(preprocess_data_test)
        preprocess_data["not_awake"] = probabilities[:, 0]
        preprocess_data["awake"] = probabilities[:, 1]

        # Làm mượt dữ liệu
        smoothing_length = 2 * 230
        preprocess_data["score"] = preprocess_data["awake"].rolling(smoothing_length, center=True).mean().fillna(method="bfill").fillna(method="ffill")
        preprocess_data["smooth"] = preprocess_data["not_awake"].rolling(smoothing_length, center=True).mean().fillna(method="bfill").fillna(method="ffill")

        # Làm tròn dữ liệu để xác định trạng thái ngủ
        preprocess_data["smooth"] = preprocess_data["smooth"].round()
        preprocess_data["event"] = self.get_event(preprocess_data)

        # Trích xuất kết quả cuối cùng
        result = preprocess_data[["series_id"]].copy()
        result["step"] = preprocess_data.index
        result["event"] = preprocess_data["event"].map({1: "wakeup", 0: "onset"})

        print(f"✅ Inference completed on {len(preprocess_data)} data rows.")
        return result
