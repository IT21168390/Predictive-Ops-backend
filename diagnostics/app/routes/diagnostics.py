from flask import Blueprint, request, jsonify
from ..utils.validation import validate_input_data
from ..models import ModelMetrics
from ..utils.data_loader import load_dataset
from ..services.fuzzy_logic import diagnose_extended
import requests

diagnostics_bp = Blueprint('diagnostics', __name__, url_prefix='/diagnostics')


@diagnostics_bp.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.json

    try:
        temp = float(data.get('temperature', 0))
        vib = float(data.get('vibration', 0))
        noise = data.get('noise')  # 'yes' or 'no'
        alignment = data.get('alignment')  # 'aligned' or 'misaligned'
        overheating = data.get('overheating')  # 'yes' or 'no'
        type = data.get('type')

        # Diagnose step-by-step
        criticality = diagnose_extended(temp, vib, noise, alignment, overheating)

        response = requests.get(f"http://51.21.194.188:5000/instructions/failure/{type}")
        if response.status_code == 200:
            instructions = response.json().get('instructions', "No instructions available.")
        else:
            instructions = "Failed to retrieve instructions. please retry again later.!"

        return jsonify({
            'criticality': criticality,
            'recommendation': instructions
        })

    except Exception as e:
        return jsonify({"error": "No suggestions found!"}), 400