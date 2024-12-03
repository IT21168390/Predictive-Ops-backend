from flask import jsonify

def validate_json(request_json, required_fields):
    """Validate incoming JSON data for required fields."""
    missing_fields = [field for field in required_fields if field not in request_json]
    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400
    return None
