from flask import Blueprint, jsonify, request

from app.services.fuzzy_logic import diagnose_extended
import requests

bp = Blueprint('diagnostics', __name__, url_prefix='/diagnostics')

@bp.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.json

    try:
        temp = float(data.get('temperature', 0))
        vib = float(data.get('vibration', 0))
        noise = data.get('noise')  # 'yes' or 'no'
        alignment = data.get('alignment')  # 'aligned' or 'misaligned'
        overheating = data.get('overheating')  # 'yes' or 'no'

        # Diagnose step-by-step
        cause = diagnose_extended(temp, vib, noise, alignment, overheating)

        response = requests.get(f"http://127.0.0.1:5000/instructions/failure/{cause}")
        if response.status_code == 200:
            instructions = response.json().get('instructions', "No instructions available.")
        else:
            instructions = "Failed to retrieve instructions. please retry again later.!"

        return jsonify({
            'cause': cause,
            'recommendation': instructions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400