from typing import Dict, Any

def validate_input_data(data: Dict[str, Any]) -> bool:
    """Validates input data for API endpoints.

    Args:
        data: Dictionary containing input data

    Returns:
        bool: True if data is valid, False otherwise
    """
    if not isinstance(data, dict):
        return False

    # Validate data for failure analysis
    if 'component' in data:
        if not isinstance(data['component'], str) or not data['component'].strip():
            return False
        if 'measurements' in data and not isinstance(data['measurements'], dict):
            return False

    # Validate data for preprocessor
    if 'data' in data:
        if not isinstance(data['data'], (list, dict)):
            return False
        if not data['data']:
            return False

    # Validate preprocessing config
    if 'config' in data:
        if not isinstance(data['config'], dict):
            return False
        valid_strategies = ['mean', 'median', 'mode', 'constant']
        if 'missing_value_strategy' in data['config']:
            if data['config']['missing_value_strategy'] not in valid_strategies:
                return False

    return True

from flask import jsonify

def validate_json(request_json, required_fields):
    """Validate incoming JSON data for required fields."""
    missing_fields = [field for field in required_fields if field not in request_json]
    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400
    return None