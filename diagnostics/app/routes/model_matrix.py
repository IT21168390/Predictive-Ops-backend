from flask import Blueprint, request, jsonify
from ..services.failure_analysis import FailureAnalysisService
from ..utils.validation import validate_input_data
from ..models import ModelMetrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, log_loss
import joblib
import pandas as pd
import numpy as np
import os

model_matrix_bp = Blueprint('model_matrix', __name__)
service = FailureAnalysisService()

# Configure paths and load model/data
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'prediction_model.pkl')
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dataset', 'dataset1.csv')

def preprocess_data(data):
    """Preprocess the data following the notebook steps"""
    # Create Combined Label
    data['Combined_Label'] = data.apply(
        lambda row: 'No Failure' if row['Target'] == 0 else row['Failure Type'], 
        axis=1
    )
    
    # Encode labels
    data['Label_Encoded'] = pd.Categorical(data['Combined_Label']).codes
    
    # Create failure type mapping
    failure_type_mapping = data[['Label_Encoded', 'Failure Type']].drop_duplicates().set_index('Label_Encoded')
    
    # Drop unnecessary columns
    processed_data = data.drop(columns=['Failure Type', 'Target', 'Combined_Label', 'Timestamp'])
    
    # Split features and target
    X = processed_data.drop(columns=['Label_Encoded'])
    y = processed_data['Label_Encoded']
    
    return X, y, failure_type_mapping

@model_matrix_bp.route("/model_metrics", methods=["GET"])
def get_model_metrics():
    """
    API endpoint to fetch model evaluation metrics with preprocessed data.
    Returns:
        JSON: Accuracy, Precision, Recall, F1-Score, Loss
    """
    try:
        # Load and preprocess data
        test_data = pd.read_csv(DATA_PATH)
        X, y, failure_mapping = preprocess_data(test_data)
        
        # Load model
        model = joblib.load(MODEL_PATH)
        
        # Generate predictions
        y_pred = model.predict(X)
        y_prob = model.predict_proba(X)
        
        # Calculate metrics
        metrics = {
            "accuracy": round(accuracy_score(y, y_pred), 4),
            "precision": round(precision_score(y, y_pred, average='weighted'), 4),
            "recall": round(recall_score(y, y_pred, average='weighted'), 4),
            "f1_score": round(f1_score(y, y_pred, average='weighted'), 4),
            "loss": round(log_loss(y, y_prob), 4)
        }
        
        # Add failure type mapping for reference
        failure_types = failure_mapping.to_dict()['Failure Type']
        
        return jsonify({
            "status": "success", 
            "metrics": metrics,
            "failure_types": failure_types
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

