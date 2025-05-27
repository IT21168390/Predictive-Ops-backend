from flask import Blueprint, request, jsonify
from ..services.failure_analysis import FailureAnalysisService
from ..utils.validation import validate_input_data
from ..models import AnalyticsResult
import pandas as pd
import shap
import joblib
import os

analytics_bp = Blueprint('analytics', __name__)
service = FailureAnalysisService()

# Load model and create SHAP explainer
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "model.pkl")
model = joblib.load(MODEL_PATH)
explainer = shap.TreeExplainer(model)

@analytics_bp.route('/analyze', methods=['POST'])
def analyze_data():
    try:
        input_data = request.json
        print("input data : ", input_data)
        
        # Convert input JSON to DataFrame
        sample_df = pd.DataFrame([input_data])

        # Drop target and failure type columns if present
        columns_to_drop = ['Target']
        sample_df = sample_df.drop(columns=[col for col in columns_to_drop if col in sample_df.columns], errors='ignore')
        print(sample_df)

        # Calculate SHAP values
        shap_values = explainer(sample_df)
        print("shap values : ", shap_values)
        
        # Convert to dictionary for JSON response
        contributions = dict(zip(sample_df.columns, shap_values[0].values.tolist()))
        print("contributions : ", contributions)

        return jsonify({
            "expected_value": float(explainer.expected_value[1]),
            "contributions": contributions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/trends', methods=['GET'])
def get_trends():
    try:
        component = request.args.get('component')
        time_range = request.args.get('time_range', 'week')
        
        trends = service.get_trends(component, time_range)
        return jsonify(trends), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/summary', methods=['GET'])
def get_summary():
    try:
        summary = service.get_analytics_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500