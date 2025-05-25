import shap
import joblib
import os
import pandas as pd

# Configure model path
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "model.pkl")

class ShapExplainer:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.explainer = shap.TreeExplainer(self.model)

    def get_shap_values(self, input_data):
        sample_df = pd.DataFrame([input_data])
        shap_values = self.explainer.shap_values(sample_df)
        contributions = dict(zip(sample_df.columns, shap_values[0]))
        expected_value = float(self.explainer.expected_value[1])
        return [contributions, expected_value]
