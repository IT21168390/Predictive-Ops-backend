from flask import Blueprint, request, jsonify
from ..utils.validation import validate_input_data
import joblib
import os

feature_importance_bp = Blueprint('feature_importance', __name__, url_prefix='/model')

# Configure model path and load model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "model.pkl")
model = joblib.load(MODEL_PATH)

@feature_importance_bp.route("/feature-importance", methods=["GET"])
def get_feature_importance():
    """
    API endpoint to fetch feature importances from the trained model.
    Returns:
        JSON: Feature names and their importance scores.
    """
    try:
        # Feature importance from the model
        feature_importance = model.feature_importances_
        feature_names = ["Vibration_01", "Vibration_02", "Vibration_03", 
                         "Temperature_01", "RPM_Sensor_01"]
        
        # Combine feature names and importances
        importance_data = [
            {"feature": feature, "importance": round(importance, 4)}
            for feature, importance in zip(feature_names, feature_importance)
        ]
        
        return jsonify({"status": "success", "feature_importances": importance_data}), 200

    except AttributeError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}), 500