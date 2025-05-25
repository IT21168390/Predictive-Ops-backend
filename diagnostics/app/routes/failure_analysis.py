from flask import Blueprint, request, jsonify
from ..services.failure_analysis import FailureAnalysisService
from ..utils.validation import validate_input_data
from ..models import FailureAnalysis

failure_analysis_bp = Blueprint('failure_analysis', __name__)
service = FailureAnalysisService()

@failure_analysis_bp.route('/predict', methods=['POST'])
def predict_failure():
    try:
        data = request.get_json()
        if not validate_input_data(data):
            return jsonify({'error': 'Invalid input data'}), 400

        prediction = service.predict_failure(data)
        return jsonify(prediction), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@failure_analysis_bp.route('/analyze', methods=['POST'])
def analyze_component():
    try:
        data = request.get_json()
        if not validate_input_data(data):
            return jsonify({'error': 'Invalid input data'}), 400

        analysis_result = service.analyze_component(data)
        return jsonify(analysis_result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@failure_analysis_bp.route('/statistics', methods=['GET'])
def get_statistics():
    try:
        statistics = service.get_failure_statistics()
        return jsonify(statistics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@failure_analysis_bp.route('/history', methods=['GET'])
def get_failure_history():
    try:
        component = request.args.get('component')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        history = service.get_failure_history(component, start_date, end_date)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Add this after the existing routes

@failure_analysis_bp.route('/test', methods=['GET'])
def test_endpoint():
    try:
        sample_response = {
            "status": "success",
            "timestamp": "2025-05-18T10:00:00",
            "sample_data": {
                "component_health": "good",
                "failure_probability": 0.05,
                "last_maintenance": "2025-05-01",
                "next_maintenance_due": "2025-06-01"
            },
            "version": "1.0"
        }
        return jsonify(sample_response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500