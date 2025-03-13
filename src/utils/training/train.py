import mlflow
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score

from logs import log
from src.utils.mlflow_utils import generate_run_name_by_date_time, activate_mlflow, log_model
from src.utils.feature.feature_extractor import make_features
import gc

class Trainer:
    def __init__(self, cfg):
        """
        Khởi tạo Trainer với config và dữ liệu.
        """
        self.cfg = cfg
        self.experiment_name = cfg["experiment_name"]
        self.run_name = generate_run_name_by_date_time()

        # Load dữ liệu từ Parquet
        self.data = pd.read_parquet(cfg["training_data"])

        # Khởi tạo mô hình RandomForestClassifier
        self.model = RandomForestClassifier(
            n_estimators=cfg["hyperparameters"]["n_estimators"],
            min_samples_leaf=cfg["hyperparameters"]["min_samples_leaf"],
            random_state=cfg["hyperparameters"]["random_state"],
            n_jobs=cfg["hyperparameters"]["n_jobs"]
        )

    def prepare_data(self, features):
        """
        Chuẩn bị dữ liệu huấn luyện và kiểm tra.
        """
        log.info("🔄 Chuẩn bị dữ liệu train/test...")
        train   = make_features(self.data)

        X = train[features]
        y = train["event"]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        log.info(f"✅ Dữ liệu train/test được chuẩn bị! Train: {self.X_train.shape}, Test: {self.X_test.shape}")

    def fit(self):
        """
        Huấn luyện mô hình RandomForest và log vào MLflow.
        """
        log.info("🚀 Bắt đầu training...")

        with activate_mlflow(experiment_name=self.experiment_name, run_name=self.run_name):
            # Ghi nhận hyperparameters vào MLflow
            mlflow.log_params(self.cfg["hyperparameters"])

            # Huấn luyện mô hình
            self.model.fit(self.X_train, self.y_train)
            del self.X_train, self.y_train
            gc.collect()
            # Dự đoán
            y_pred = self.model.predict(self.X_test)

            # Tính toán metrics
            mse = mean_squared_error(self.y_test, y_pred)
            r2 = r2_score(self.y_test, y_pred)
            accuracy = accuracy_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred)

            # Log metrics vào MLflow
            mlflow.log_metrics({
                "mse": mse,
                "r2_score": r2,
                "accuracy": accuracy,
                "f1_score": f1
            })

            log.info(f"✅ Training hoàn tất! Accuracy={accuracy:.4f}, F1 Score={f1:.4f}")

            # Lưu mô hình
            model_path = "./src/weight/random_forest.pkl"
            dump(self.model, model_path)
            mlflow.sklearn.log_model(self.model, "random_forest_model")

            # Đăng ký model vào MLflow Registry
            log_model(model_path, "random_forest_model")

        