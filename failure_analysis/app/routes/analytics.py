from flask import Blueprint, jsonify, request
from app.services.shap_explainer import get_shap_values
import pandas as pd
import shap
import joblib

bp = Blueprint('analytics', __name__, url_prefix='/analytics')


MODEL_PATH = "./model.pkl"
model = joblib.load(MODEL_PATH)
explainer = shap.TreeExplainer(model)

@bp.route('/analyze', methods=['POST'])
def analyze():
    input_data = request.json
    sample_df = pd.DataFrame([input_data])  # Convert input JSON to DataFrame

    # Drop target and failure type columns if present
    columns_to_drop = ['Target']
    sample_df = sample_df.drop(columns=[col for col in columns_to_drop if col in sample_df.columns], errors='ignore')
    print(sample_df)
    shap_values = explainer(sample_df)
    print("shap vcal  : ", shap_values)
    contributions = dict(zip(sample_df.columns, shap_values[0].values.tolist()))  # Convert to list
    print("con : ", contributions)
    return jsonify({
        "expected_value": float(explainer.expected_value[1]),  # Ensure it's JSON serializable
        "contributions": contributions
    })

