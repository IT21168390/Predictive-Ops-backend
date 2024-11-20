import shap
import pandas as pd
import joblib

MODEL_PATH = "./model.pkl"
model = joblib.load(MODEL_PATH)
explainer = shap.TreeExplainer(model)

def get_shap_values(input_data):
    sample_df = pd.DataFrame([input_data])
    shap_values = explainer.shap_values(sample_df)
    contributions = dict(zip(sample_df.columns, shap_values[0]))
    expected_value = float(explainer.expected_value[1])
    return [contributions, expected_value]
