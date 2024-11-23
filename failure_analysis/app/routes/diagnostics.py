from flask import Blueprint, jsonify, request

from app.services.fuzzy_logic import diagnose_extended

bp = Blueprint('diagnostics', __name__, url_prefix='/diagnostics')

@bp.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.json

    try:
        temp = float(data.get('temperature', 0))
        vib = float(data.get('vibration', 0))
        noise = data.get('noise') 
        alignment = data.get('alignment') 
        overheating = data.get('overheating')

        cause = diagnose_extended(temp, vib, noise, alignment, overheating)

        return jsonify({
            'cause': cause,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400