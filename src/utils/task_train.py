from src.utils.training.train import Trainer
from configs import cfg
from logs import log

def run_training():
    """
    Chạy quá trình huấn luyện và validation mô hình RandomForest.
    """
    log.info("🚀 Bắt đầu quá trình huấn luyện mô hình...")

    # Khởi tạo Trainer
    trainer = Trainer(cfg)

    # Chuẩn bị dữ liệu với danh sách features
    features = [
        "hour", "anglez", "anglez_rolling_mean", "anglez_rolling_max", "anglez_rolling_std",
        "anglez_diff", "anglez_diff_rolling_mean", "anglez_diff_rolling_max",
        "enmo", "enmo_rolling_mean", "enmo_rolling_max", "enmo_rolling_std",
        "enmo_diff", "enmo_diff_rolling_mean", "enmo_diff_rolling_max"
    ]
    
    trainer.prepare_data(features)

    # Huấn luyện mô hình
    trainer.fit()

    log.info("✅ Quá trình huấn luyện hoàn tất!")

if __name__ == "__main__":
    run_training()
