import joblib
import pandas as pd
from src.utils.feature.feature_extractor import make_features
from itertools import groupby

class InferenceData:
    def __init__(self, weight_path: str):
        """
        Load the model from the specified weight_path.
        """
        try:
            self.model = joblib.load(weight_path)
        except Exception as e:
            raise ValueError(f"❌ Unable to load model from {weight_path}. Error: {e}")

        # List of required features for the model
        self.features = [
            "hour", "anglez", "anglez_rolling_mean", "anglez_rolling_max", "anglez_rolling_std",
            "anglez_diff", "anglez_diff_rolling_mean", "anglez_diff_rolling_max",
            "enmo", "enmo_rolling_mean", "enmo_rolling_max", "enmo_rolling_std",
            "enmo_diff", "enmo_diff_rolling_mean", "enmo_diff_rolling_max",
        ]

    @staticmethod
    def get_event(df):
        """
        Identify onset and wakeup events based on the 'smooth' label.
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
        Process the input data, extract features, and perform inference.
        Returns a DataFrame containing only the columns ['series_id', 'step', 'event'].
        """
        if data.empty:
            raise ValueError("❌ Input data is empty! Please provide valid data.")

        # Preprocess data
        preprocess_data = make_features(data)

        # Check if all required features are available
        missing_features = [f for f in self.features if f not in preprocess_data.columns]
        if missing_features:
            raise ValueError(f"❌ Missing the following required features: {missing_features}")

        # Extract input data for the model
        preprocess_data_test = preprocess_data[self.features]

        # Predict probabilities
        probabilities = self.model.predict_proba(preprocess_data_test)
        preprocess_data["not_awake"] = probabilities[:, 0]
        preprocess_data["awake"] = probabilities[:, 1]

        # Smooth the data
        smoothing_length = 2 * 230
        preprocess_data["score"] = preprocess_data["awake"].rolling(smoothing_length, center=True).mean().fillna(method="bfill").fillna(method="ffill")
        preprocess_data["smooth"] = preprocess_data["not_awake"].rolling(smoothing_length, center=True).mean().fillna(method="bfill").fillna(method="ffill")

        # Round values to determine the state
        preprocess_data["smooth"] = preprocess_data["smooth"].round()
        preprocess_data["event"] = self.get_event(preprocess_data)

        # Filter the output to include only the desired columns
        result = preprocess_data[["series_id"]].copy()
        result["step"] = preprocess_data.index

        # Map event values: 1 -> 'wakeup', 0 -> 'onset'
        result["event"] = preprocess_data["event"].map({1: "wakeup", 0: "onset"})

        print(f"✅ Inference completed on {len(preprocess_data)} data rows.")
        return result
